# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

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
from .client import client
from .errors import JujuError


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
    # Set it to ~/.local/share/juju as default
    config_dir = Path('~/.local/share/juju')

    # Check $JUJU_DATA
    if juju_data := os.environ.get('JUJU_DATA'):
        config_dir = Path(juju_data)
    # Secondly check: $XDG_DATA_HOME for ~/.local/share
    elif xdg_data_home := os.environ.get('XDG_DATA_HOME'):
        config_dir = Path(xdg_data_home) / 'juju'

    return str(config_dir.expanduser().resolve())


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
    await jasyncio.shield(jasyncio.wait_for(_block(), timeout))


async def block_until_with_coroutine(condition_coroutine, timeout=None, wait_period=0.5):
    """Return only after the given coroutine returns True.
    If a timeout occurs, it cancels the task and raises
    asyncio.TimeoutError.
    """
    async def _block():
        while not await condition_coroutine():
            await jasyncio.sleep(wait_period)
    await jasyncio.shield(jasyncio.wait_for(_block(), timeout=timeout))


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
    for f in pending:
        try:
            await f
        except jasyncio.CancelledError:
            pass
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
    "metadata.yaml", or "manifest.yaml", or "charmcraft.yaml"

    :return: Object of charm metadata
    """
    if str(path).endswith('.charm'):
        with zipfile.ZipFile(str(path), 'r') as charm_file:
            metadata = yaml.load(charm_file.read(yaml_file), Loader=yaml.FullLoader)
    else:
        entity_path = Path(path)
        metadata_path = entity_path / yaml_file
        if not metadata_path.exists():
            return {}
        metadata = yaml.load(metadata_path.read_text(), Loader=yaml.FullLoader)

    return metadata


def get_local_charm_metadata(path):
    return get_local_charm_data(path, 'metadata.yaml')


def get_local_charm_manifest(path):
    return get_local_charm_data(path, 'manifest.yaml')


def get_local_charm_charmcraft_yaml(path):
    return get_local_charm_data(path, 'charmcraft.yaml')


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
LUNAR = "lunar"
MANTIC = "mantic"

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
    LUNAR: "23.04",
    MANTIC: "23.10",
}

KUBERNETES = "kubernetes"
KUBERNETES_SERIES = {
    KUBERNETES: "kubernetes"
}

ALL_SERIES_VERSIONS = {**UBUNTU_SERIES, **KUBERNETES_SERIES}


def get_series_version(series_name):
    """get_series_version outputs the version of the OS based on the given series
    e.g. jammy -> 22.04, kubernetes -> kubernetes

    :param str series_name: name of the series
    :return str: os version
    """
    if series_name not in ALL_SERIES_VERSIONS:
        raise errors.JujuError("Unknown series : %s", series_name)
    return ALL_SERIES_VERSIONS[series_name]


def get_version_series(version):
    """get_version_series is the opposite of the get_series_version. It outputs the series based
    on given OS version

    :param str version: version of the OS
    return str: name of the series corresponding to the given version
    """
    if version not in UBUNTU_SERIES.values():
        raise errors.JujuError("Unknown version : %s", version)
    return list(UBUNTU_SERIES.keys())[list(UBUNTU_SERIES.values()).index(version)]


def get_local_charm_base(series, charm_path, base_class):
    """Deduce the base [channel/osname] of a local charm based on what we
    know already

    :param str series: This may come from the argument or the metadata.yaml
    :param str charm_path: Path of charm directory/.charm file
    :param class base_class:
    :return: Instance of the baseCls with channel/osname informaiton
    """

    channel_for_base = ''
    os_name_for_base = ''

    # We should know the series, so use it to get a channel
    if series:
        channel_for_base = get_series_version(series) if series else ''
        if channel_for_base:
            # we currently only support ubuntu series (statically)
            # TODO (cderici) : go juju/core/series/supported.go and get the
            #  others here too
            if series in KUBERNETES_SERIES:
                os_name_for_base = 'kubernetes'
            else:
                os_name_for_base = 'ubuntu'

    # Check the charm manifest
    if channel_for_base == '':
        charm_manifest = get_local_charm_manifest(charm_path)
        if 'bases' in charm_manifest:
            channel_for_base = charm_manifest['bases'][0]['channel']
            os_name_for_base = charm_manifest['bases'][0]['name']

    # Also check the charmcraft.yaml
    if channel_for_base == '':
        charmcraft_yaml = get_local_charm_charmcraft_yaml(charm_path)
        if 'bases' in charmcraft_yaml:
            channel_for_base = charmcraft_yaml['bases'][0]['run-on'][0]['channel']
            os_name_for_base = charmcraft_yaml['bases'][0]['run-on'][0]['name']

    if channel_for_base == '':
        raise errors.JujuError("Unable to determine base for charm : %s" %
                               charm_path)

    # Legacy k8s charms - assume ubuntu focal
    # as per juju/cmd/juju/application/utils.DeduceOrigin()
    if channel_for_base == "kubernetes" or os_name_for_base == "kubernetes":
        channel_for_base = '20.04/stable'
        os_name_for_base = 'ubuntu'
    return base_class(channel_for_base, os_name_for_base)


def base_channel_to_series(channel):
    """Returns the series string using the track inside the base channel

    :param str channel: is track/risk (e.g. 20.04/stable)
    :return: str series (e.g. focal)
    """
    return get_version_series(origin.Channel.parse(channel).track)


def parse_base_arg(base):
    """Parses a given base into a Client.Base object
    :param base str : The base to deploy a charm (e.g. ubuntu@22.04)
    """
    client.CharmBase()
    if not (isinstance(base, str) and "@" in base):
        raise errors.JujuError(f"expected base string to contain os and channel separated by '@', got : {base}")

    name, channel = base.split('@')
    return client.Base(name=name, channel=channel)


DEFAULT_SUPPORTED_LTS = 'jammy'
DEFAULT_SUPPORTED_LTS_BASE = client.Base(channel='22.04', name='ubuntu')


def base_channel_from_series(track, risk, series):
    return origin.Channel(track=track, risk=risk).normalize().compute_base_channel(series=series)


def get_os_from_series(series):
    if series in UBUNTU_SERIES:
        return 'ubuntu'
    raise JujuError(f'os for the series {series} needs to be added')


def get_base_from_origin_or_channel(origin_or_channel, series=None):
    channel, os_name = None, None
    if series:
        channel = base_channel_from_series(origin_or_channel.track, origin_or_channel.risk, series)
        os_name = get_os_from_series(series)
    return client.Base(channel=channel, name=os_name)


def series_for_charm(requested_series, supported_series):
    """series_for_charm takes a requested series and a list of series supported by a
    charm and returns the series which is relevant.
    If the requested series is empty, then the first supported series is used,
    otherwise the requested series is validated against the supported series.
    """
    if len(supported_series) == 1 and supported_series[0] == '':
        raise JujuError("invalid supported series reported by charm : ['']")
    if len(supported_series) == 0:
        if requested_series == '':
            raise JujuError("missing series")
        return requested_series

    # use the charm default
    if requested_series == '':
        return supported_series[-1]

    for s in supported_series:
        if requested_series == s:
            return requested_series
    raise JujuError(f'requested series {requested_series} is not among the supported series {supported_series}')


def user_requested(series_arg, supported_series, force):
    series = series_for_charm(series_arg, supported_series)
    if force:
        series = series_arg
    # Todo (cderici): validate the series with workload_series to see if juju is supporting that
    return series


def series_selector(series_arg='', charm_url=None, model_config=None, supported_series=[], force=False):
    """
    series_selector corresponds to the CharmSeries() in
    https://github.com/juju/juju/blob/develop/core/charm/series_selector.go

    determines what series to use with a charm.
    Order of preference is:
    - user requested with --series or defined by bundle when deploying
    - user requested in charm's url (e.g. juju deploy jammy/ubuntu)
    - model default, if set, acts like --series
    - default from charm metadata supported series / series in url
    - default LTS
    """

    # User has requested a series with --series.
    if series_arg:
        return user_requested(series_arg, supported_series, force)

    # User specified a series in the charm URL, e.g.
    # juju deploy precise/ubuntu.
    if charm_url and charm_url.series:
        return user_requested(charm_url.series, supported_series, force)

    # No series explicitly requested by the user.
    # Use model default series, if explicitly set and supported by the charm.
    if model_config and model_config['default-base'].value:
        default_base = model_config['default-base'].value
        base = parse_base_arg(default_base)
        series = base_channel_to_series(base.channel)
        return user_requested(series, supported_series, force)

    # Next fall back to the charm's list of series, filtered to what's supported
    # by Juju. Preserve the order of the supported series from the charm
    # metadata, as the order could be out of order compared to Ubuntu series
    # order (precise, xenial, bionic, trusty, etc).
    try:
        # TODO (cderici): restrict the supported_series with JujuSupportedSeries
        return user_requested('', supported_series, force)
    except JujuError:
        pass

    # Charm hasn't specified a default (likely due to being a local charm
    # deployed by path). Last chance, best we can do is default to LTS.
    return DEFAULT_SUPPORTED_LTS


def should_upgrade_resource(available_resource, existing_resources, arg_resources={}):
    """Called in the context of upgrade_charm. Given a resource R, takes a look at the resources we
    already have and decides if we need to refresh R.

    :param dict[str] available_resource: The dict representing the client.Resource coming from the
    charmhub api. We're considering if we need to refresh this during upgrade_charm.
    :param dict[str] existing_resources: The dict coming from resources_facade.ListResources
    representing the resources of the currently deployed charm.
    :param dict[str] arg_resources: user provided resources to be refreshed

    :result bool: The decision to refresh the given resource
    """

    # should upgrade resource?
    res_name = available_resource.get('Name', available_resource.get('name'))

    if res_name in arg_resources:
        return True

    # do we have it already?
    if res_name in existing_resources:
        # no upgrade, if it's upload
        if existing_resources[res_name].origin == 'upload':
            return False
        # no upgrade, if upstream doesn't have a newer revision of the resource available
        available_rev = available_resource.get('Revision', available_resource.get('revision', -1))
        u_fields = existing_resources[res_name].unknown_fields
        existing_rev = u_fields.get('Revision', u_fields.get('revision', -1))
        if existing_rev >= available_rev:
            return False
    return True
