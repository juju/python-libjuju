import os
import textwrap
from collections import defaultdict
from functools import partial
from pathlib import Path
import base64
from pyasn1.type import univ, char
from pyasn1.codec.der.encoder import encode
import yaml
import zipfile

from . import jasyncio, origin, errors


async def execute_process(*cmd, log=None):
    '''
    Wrapper around asyncio.create_subprocess_exec.

    '''
    p = await jasyncio.create_subprocess_exec(
        *cmd,
        stdin=jasyncio.subprocess.PIPE,
        stdout=jasyncio.subprocess.PIPE,
        stderr=jasyncio.subprocess.PIPE)
    stdout, stderr = await p.communicate()
    if log:
        log.debug("Exec %s -> %d", cmd, p.returncode)
        if stdout:
            log.debug(stdout.decode('utf-8'))
        if stderr:
            log.debug(stderr.decode('utf-8'))
    return p.returncode == 0


def juju_config_dir():
    """Resolves and returns the path string to the juju configuration
    folder for the juju CLI tool. Of the following items, returns the
    first option that works (top to bottom):

    * $JUJU_DATA
    * $XDG_DATA_HOME/juju
    * ~/.local/share/juju

    """
    # Check $JUJU_DATA first
    config_dir = os.environ.get('JUJU_DATA', None)

    # Second option: $XDG_DATA_HOME for ~/.local/share
    if not config_dir:
        config_dir = os.environ.get('XDG_DATA_HOME', None)

    # Third option: just set it to ~/.local/share/juju
    if not config_dir:
        config_dir = '~/.local/share/juju'

    return os.path.abspath(os.path.expanduser(config_dir))


def juju_ssh_key_paths():
    """Resolves and returns the path strings for public and private ssh
    keys for juju CLI.

    """
    config_dir = juju_config_dir()
    public_key_path = os.path.join(config_dir, 'ssh', 'juju_id_rsa.pub')
    private_key_path = os.path.join(config_dir, 'ssh', 'juju_id_rsa')

    return public_key_path, private_key_path


def _read_ssh_key():
    '''
    Inner function for read_ssh_key, suitable for passing to our
    Executor.

    '''
    public_key_path_str, _ = juju_ssh_key_paths()
    ssh_key_path = Path(public_key_path_str)
    with ssh_key_path.open('r') as ssh_key_file:
        ssh_key = ssh_key_file.readlines()[0].strip()
    return ssh_key


async def read_ssh_key():
    '''
    Attempt to read the local juju admin's public ssh key, so that it
    can be passed on to a model.

    '''
    loop = jasyncio.get_running_loop()
    return await loop.run_in_executor(None, _read_ssh_key)


class IdQueue:
    """
    Wrapper around asyncio.Queue that maintains a separate queue for each ID.
    """

    def __init__(self, maxsize=0):
        self._queues = defaultdict(partial(jasyncio.Queue, maxsize))

    async def get(self, id):
        value = await self._queues[id].get()
        del self._queues[id]
        if isinstance(value, Exception):
            raise value
        return value

    async def put(self, id, value):
        await self._queues[id].put(value)

    async def put_all(self, value):
        for queue in self._queues.values():
            await queue.put(value)


async def block_until(*conditions, timeout=None, wait_period=0.5):
    """Return only after all conditions are true.
    If a timeout occurs, it cancels the task and raises
    asyncio.TimeoutError.

    """
    async def _block():
        while not all(c() for c in conditions):
            await jasyncio.sleep(wait_period)
    await jasyncio.wait_for(_block(), timeout)


async def block_until_with_coroutine(condition_coroutine, timeout=None, wait_period=0.5):
    """Return only after the given coroutine returns True.
    If a timeout occurs, it cancels the task and raises
    asyncio.TimeoutError.
    """
    async def _block():
        while not await condition_coroutine():
            await jasyncio.sleep(wait_period)
    await jasyncio.wait_for(_block(), timeout=timeout)


async def wait_for_bundle(model, bundle, **kwargs):
    """Helper to wait for just the apps in a specific bundle.

    Equivalent to loading the bundle, pulling out the app names, and calling::

        await model.wait_for_idle(app_names, **kwargs)
    """
    try:
        bundle_path = Path(bundle)
        if bundle_path.is_file():
            bundle = bundle_path.read_text()
        elif (bundle_path / "bundle.yaml").is_file():
            bundle = (bundle_path / "bundle.yaml")
    except OSError:
        pass
    bundle = yaml.safe_load(textwrap.dedent(bundle).strip())
    apps = list(bundle.get("applications", bundle.get("services")).keys())
    await model.wait_for_idle(apps, **kwargs)


async def run_with_interrupt(task, *events, log=None):
    """
    Awaits a task while allowing it to be interrupted by one or more
    `asyncio.Event`s.

    If the task finishes without the events becoming set, the results of the
    task will be returned.  If the event become set, the task will be cancelled
    ``None`` will be returned.

    :param task: Task to run
    :param events: One or more `asyncio.Event`s which, if set, will interrupt
        `task` and cause it to be cancelled.
    """
    task = jasyncio.create_task_with_handler(task, 'tmp', log)
    event_tasks = [jasyncio.ensure_future(event.wait()) for event in events]
    done, pending = await jasyncio.wait([task] + event_tasks,
                                        return_when=jasyncio.FIRST_COMPLETED)
    for f in pending:
        f.cancel()  # cancel unfinished tasks
    for f in done:
        f.exception()  # prevent "exception was not retrieved" errors
    if task in done:
        return task.result()  # may raise exception
    else:
        return None


class Addrs(univ.SequenceOf):
    componentType = char.PrintableString()


class RegistrationInfo(univ.Sequence):
    """
    ASN.1 representation of:

    type RegistrationInfo struct {
    User string

        Addrs []string

        SecretKey []byte

        ControllerName string
    }
    """
    pass


def generate_user_controller_access_token(username, controller_endpoints, secret_key, controller_name):
    """" Implement in python what is currently done in GO
    https://github.com/juju/juju/blob/a5ab92ec9b7f5da3678d9ac603fe52d45af24412/cmd/juju/user/utils.go#L16

    :param username: name of the user to register
    :param controller_endpoints: juju controller endpoints list in the format <ip>:<port>
    :param secret_key: base64 encoded string of the secret-key generated by juju
    :param controller_name: name of the controller to register to.
    """

    # Secret key is returned as base64 encoded string in:
    # https://websockets.readthedocs.io/en/stable/_modules/websockets/protocol.html#WebSocketCommonProtocol.recv
    # Deconding it before marshalling into the ASN.1 message
    secret_key = base64.b64decode(secret_key)
    addr = Addrs()
    for endpoint in controller_endpoints:
        addr.append(endpoint)

    registration_string = RegistrationInfo()
    registration_string.setComponentByPosition(0, char.PrintableString(username))
    registration_string.setComponentByPosition(1, addr)
    registration_string.setComponentByPosition(2, univ.OctetString(secret_key))
    registration_string.setComponentByPosition(3, char.PrintableString(controller_name))
    registration_string = encode(registration_string)
    remainder = len(registration_string) % 3
    registration_string += b"\0" * (3 - remainder)
    return base64.urlsafe_b64encode(registration_string)


def get_local_charm_data(path, yaml_file):
    """Retrieve Metadata of a Charm from its path

    :patam str path: Path of charm directory or .charm file
    :patam str yaml_file: name of the yaml file, can be either
    "metadata.yaml", or "manifest.yaml"

    :return: Object of charm metadata
    """
    if str(path).endswith('.charm'):
        with zipfile.ZipFile(str(path), 'r') as charm_file:
            metadata = yaml.load(charm_file.read(yaml_file), Loader=yaml.FullLoader)
    else:
        entity_path = Path(path)
        metadata_path = entity_path / yaml_file
        metadata = yaml.load(metadata_path.read_text(), Loader=yaml.FullLoader)

    return metadata


def get_local_charm_metadata(path):
    return get_local_charm_data(path, 'metadata.yaml')


def get_local_charm_manifest(path):
    return get_local_charm_data(path, 'manifest.yaml')


PRECISE = "precise"
QUANTAL = "quantal"
RARING = "raring"
SAUCY = "saucy"
TRUSTY = "trusty"
UTOPIC = "utopic"
VIVID = "vivid"
WILY = "wily"
XENIAL = "xenial"
YAKKETY = "yakkety"
ZESTY = "zesty"
ARTFUL = "artful"
BIONIC = "bionic"
COSMIC = "cosmic"
DISCO = "disco"
EOAN = "eoan"
FOCAL = "focal"
GROOVY = "groovy"
HIRSUTE = "hirsute"
IMPISH = "impish"
JAMMY = "jammy"
KINETIC = "kinetic"

UBUNTU_SERIES = {
    PRECISE: "12.04",
    QUANTAL: "12.10",
    RARING: "13.04",
    SAUCY: "13.10",
    TRUSTY: "14.04",
    UTOPIC: "14.10",
    VIVID: "15.04",
    WILY: "15.10",
    XENIAL: "16.04",
    YAKKETY: "16.10",
    ZESTY: "17.04",
    ARTFUL: "17.10",
    BIONIC: "18.04",
    COSMIC: "18.10",
    DISCO: "19.04",
    EOAN: "19.10",
    FOCAL: "20.04",
    GROOVY: "20.10",
    HIRSUTE: "21.04",
    IMPISH: "21.10",
    JAMMY: "22.04",
    KINETIC: "22.10",
}


def get_series_version(series_name):
    if series_name not in UBUNTU_SERIES:
        raise errors.JujuError("Unknown series : %s", series_name)
    return UBUNTU_SERIES[series_name]


def get_version_series(version):
    if version not in UBUNTU_SERIES.values():
        raise errors.JujuError("Unknown version : %s", version)
    return list(UBUNTU_SERIES.keys())[list(UBUNTU_SERIES.values()).index(version)]


def get_local_charm_base(series, channel_from_arg, charm_metadata,
                         charm_path, baseCls):
    """Deduce the base [channel/osname] of a local charm based on what we
    know already

    :param str series: This may come from the argument or the metadata.yaml
    :param str channel_from_arg: This is channel passed as argument, if any.
    :param dict charm_metadata: metadata.yaml
    :param str charm_path: Path of charm directory/.charm file
    :param class baseCls:
    :return: Instance of the baseCls with channel/osname informaiton
    """

    channel_for_base = ''
    os_name_for_base = ''
    # If user passed a channel_arg, then check the supported series against
    # the channel's track
    chnl_check = origin.Channel.parse(channel_from_arg) if channel_from_arg \
        else None
    if chnl_check:
        not_supported_error = errors.JujuError(
            "Given channel [track/risk] is not supported --"
            "\n - Given channel : %s"
            "\n - Series in Charm Metadata : %s" %
            (channel_from_arg, charm_metadata['series']))
        channel_for_base = chnl_check.track
        intented_series = get_version_series(channel_for_base)
        if intented_series not in charm_metadata['series']:
            raise not_supported_error
        # Also check the manifest if there's one
        charm_manifest = get_local_charm_manifest(charm_path)
        if 'bases' in charm_manifest:
            for base in charm_manifest['bases']:
                if channel_for_base == base['channel']:
                    break
            else:
                raise not_supported_error

    # If we know the series, use it to get a channel
    if channel_for_base == '':
        channel_for_base = get_series_version(series) if series else ''
        if channel_for_base:
            # we currently only support ubuntu series (statically)
            # TODO (cderici) : go juju/core/series/supported.go and get the
            #  others here too
            os_name_for_base = 'ubuntu'

    # Check the charm manifest
    if channel_for_base == '':
        charm_manifest = get_local_charm_manifest(charm_path)
        if 'bases' in charm_manifest:
            channel_for_base = charm_manifest['bases'][0]['channel']
            os_name_for_base = charm_manifest['bases'][0]['name']

    if channel_for_base == '':
        raise errors.JujuError("Unable to determine base for charm : %s" %
                               charm_path)

    return baseCls(channel_for_base, os_name_for_base)


def base_channel_to_series(channel):
    """Returns the series string using the track inside the base channel

    :param str channel: is track/risk (e.g. 20.04/stable)
    :return: str series (e.g. focal)
    """
    return get_version_series(origin.Channel.parse(channel).track)
