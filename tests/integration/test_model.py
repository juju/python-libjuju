import json
import os
import random
import string
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import mock
import paramiko

import pylxd
import pytest
from juju import jasyncio, tag
from juju.client import client
from juju.errors import JujuError, JujuModelError, JujuUnitError, JujuConnectionError
from juju.model import Model, ModelObserver
from juju.utils import block_until, run_with_interrupt, wait_for_bundle, base_channel_to_series

from .. import base

MB = 1
GB = 1024
SSH_KEY = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsYMJGNGG74HAJha3n2CFmWYsOOaORnJK6VqNy86pj0MIpvRXBzFzVy09uPQ66GOQhTEoJHEqE77VMui7+62AcMXT+GG7cFHcnU8XVQsGM6UirCcNyWNysfiEMoAdZScJf/GvoY87tMEszhZIUV37z8PUBx6twIqMdr31W1J0IaPa+sV6FEDadeLaNTvancDcHK1zuKsL39jzAg7+LYjKJfEfrsQP+lj/EQcjtKqlhVS5kzsJVfx8ZEd0xhW5G7N6bCdKNalS8mKCMaBXJpijNQ82AiyqCIDCRrre2To0/i7pTjRiL0U9f9mV3S4NJaQaokR050w/ZLySFf6F7joJT mathijs@Qrama-Mathijs'  # noqa
HERE_DIR = Path(__file__).absolute().parent  # tests/integration
TESTS_DIR = HERE_DIR.parent  # tests/
OVERLAYS_DIR = HERE_DIR / 'bundle' / 'test-overlays'


@base.bootstrapped
@pytest.mark.asyncio
async def test_model_name(event_loop):
    model = Model()
    with pytest.raises(JujuModelError):
        model.name

    async with base.CleanModel() as new_model:
        await model.connect(new_model.name)
        assert model.name == new_model.name
        await model.disconnect()


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_bundle_dir(event_loop):
    bundle_path = TESTS_DIR / 'bundle'

    async with base.CleanModel() as model:
        await model.deploy(str(bundle_path))

        keystone = model.applications.get('keystone')
        mysql = model.applications.get('mysql-innodb')
        assert keystone and mysql
        await model.block_until(lambda: (len(keystone.units) == 1 and
                                len(mysql.units) == 1),
                                timeout=60 * 4)


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_bundle_file(event_loop):
    bundle_path = TESTS_DIR / 'bundle'
    mini_bundle_file_path = bundle_path / 'mini-bundle.yaml'

    async with base.CleanModel() as model:
        await model.deploy(str(mini_bundle_file_path))

        ghost = model.applications.get('hello-juju')
        mysql = model.applications.get('postgresql')
        assert ghost and mysql
        await model.block_until(lambda: (len(ghost.units) == 1 and
                                len(mysql.units) == 1),
                                timeout=60 * 4)


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_bundle_local_resource_relative_path(event_loop):
    bundle_file_path = HERE_DIR / 'bundle-file-resource.yaml'

    async with base.CleanModel() as model:
        await model.deploy(str(bundle_file_path))

        app = model.applications.get('file-resource-charm')
        assert app
        await model.block_until(lambda: (len(app.units) == 1),
                                timeout=60 * 4)


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_bundle_include_file(event_loop):
    bundle_dir = TESTS_DIR / 'integration' / 'bundle'
    bundle_yaml_path = bundle_dir / 'bundle-include-file.yaml'

    async with base.CleanModel() as model:
        await model.deploy(str(bundle_yaml_path))

        appa = model.applications.get('helloa', None)
        appb = model.applications.get('hellob', None)
        test = model.applications.get('test', None)
        assert appa and appb and test
        assert appa.config.get('port', None) == 666
        assert appa.config.get('application-repo', "") == "http://my-juju.com"


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_bundle_include_base64(event_loop):
    bundle_dir = TESTS_DIR / 'integration' / 'bundle'
    bundle_yaml_path = bundle_dir / 'bundle-include-base64.yaml'

    async with base.CleanModel() as model:
        await model.deploy(str(bundle_yaml_path))

        appa = model.applications.get('helloa', None)
        appb = model.applications.get('hellob', None)
        test = model.applications.get('test', None)
        assert appa and appb and test
        assert appa.config.get('application-repo', "") == "http://my-juju.com"


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_bundle_local_charms(event_loop):
    bundle_path = TESTS_DIR / 'integration' / 'bundle' / 'local.yaml'

    async with base.CleanModel() as model:
        await model.deploy(bundle_path)
        await wait_for_bundle(model, bundle_path)
        assert set(model.units.keys()) == set(['test1/0', 'test2/0'])
        assert model.units['test1/0'].agent_status == 'idle'
        assert model.units['test1/0'].workload_status == 'active'
        assert model.units['test2/0'].agent_status == 'idle'
        assert model.units['test2/0'].workload_status == 'active'


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_invalid_bundle(event_loop):
    pytest.skip('test_deploy_invalid_bundle intermittent test failure')
    bundle_path = TESTS_DIR / 'bundle' / 'invalid.yaml'
    async with base.CleanModel() as model:
        with pytest.raises(JujuError):
            await model.deploy(str(bundle_path))


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_charm(event_loop):
    charm_path = TESTS_DIR / 'charm'

    async with base.CleanModel() as model:
        await model.deploy(str(charm_path))
        assert 'charm' in model.applications
        await model.wait_for_idle(status="active")
        assert model.units['charm/0'].workload_status == 'active'


@base.bootstrapped
@pytest.mark.asyncio
async def test_wait_local_charm_blocked(event_loop):
    charm_path = TESTS_DIR / 'charm'

    async with base.CleanModel() as model:
        await model.deploy(str(charm_path), config={'status': 'blocked'})
        assert 'charm' in model.applications
        await model.wait_for_idle()
        with pytest.raises(JujuUnitError):
            await model.wait_for_idle(status="active",
                                      raise_on_blocked=True,
                                      timeout=30)


@base.bootstrapped
@pytest.mark.asyncio
async def test_wait_local_charm_waiting_timeout(event_loop):
    charm_path = TESTS_DIR / 'charm'

    async with base.CleanModel() as model:
        await model.deploy(str(charm_path), config={'status': 'waiting'})
        assert 'charm' in model.applications
        await model.wait_for_idle()
        with pytest.raises(jasyncio.TimeoutError):
            await model.wait_for_idle(status="active", timeout=30)


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_bundle(event_loop):
    async with base.CleanModel() as model:
        await model.deploy('canonical-livepatch-onprem', channel='edge', trust=True)

        for app in ('haproxy', 'livepatch', 'postgresql', 'ubuntu-advantage'):
            assert app in model.applications


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_bundle_with_overlay_multi(event_loop):
    async with base.CleanModel() as model:
        bundle_with_overlay_path = OVERLAYS_DIR / 'bundle-with-overlay-multi.yaml'
        await model.deploy(bundle_with_overlay_path)

        # this bundle deploys mysql and ghost apps and relates them,
        # but the overlay attached removes ghost, so
        assert 'mysql' in model.applications
        assert 'ghost' not in model.applications


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_bundle_with_overlay_as_argument(event_loop):
    async with base.CleanModel() as model:
        overlay_path = OVERLAYS_DIR / 'test-overlay.yaml'

        await model.deploy('juju-qa-bundle-test', overlays=[overlay_path])
        # juju-qa-bundle-test installs the applications
        #   - juju-qa-test
        #   - juju-qa-test-focal
        #   - ntp
        #   - ntp-focal

        # our overlay requests to remove ntp and add ghost and mysql
        # and relate them, so
        assert 'juju-qa-test' in model.applications
        assert 'ntp' not in model.applications
        assert 'ghost' in model.applications
        assert 'mysql' in model.applications


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_bundle_with_multi_overlay_as_argument(event_loop):
    async with base.CleanModel() as model:
        overlay_path = OVERLAYS_DIR / 'test-multi-overlay.yaml'

        await model.deploy('juju-qa-bundle-test', overlays=[overlay_path])
        assert 'ntp' not in model.applications
        assert 'memcached' not in model.applications
        assert 'mysql' in model.applications


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_bundle_with_multiple_overlays_with_include_files(event_loop):
    async with base.CleanModel() as model:
        bundle_yaml_path = TESTS_DIR / 'integration' / 'bundle' / 'bundle.yaml'
        overlay1_path = OVERLAYS_DIR / 'test-overlay2.yaml'
        overlay2_path = OVERLAYS_DIR / 'test-overlay3.yaml'

        await model.deploy(str(bundle_yaml_path), overlays=[overlay1_path, overlay2_path])
        
        assert 'influxdb' not in model.applications
        assert 'test' not in model.applications
        assert 'memcached' not in model.applications
        assert 'grafana' in model.applications


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_charm_folder_symlink(event_loop):
    charm_path = TESTS_DIR / 'charm-folder-symlink'

    async with base.CleanModel() as model:
        simple = await model.deploy(str(charm_path))
        assert 'simple' in model.applications
        terminal_statuses = ('active', 'error', 'blocked')
        await model.block_until(
            lambda: (
                len(simple.units) > 0 and
                simple.units[0].workload_status in terminal_statuses)
        )
        assert simple.units[0].workload_status == 'active'


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_trusted_bundle(event_loop):
    async with base.CleanModel() as model:
        await model.deploy('canonical-livepatch-onprem', channel='stable', trust=True)

        for app in ('haproxy', 'livepatch', 'postgresql', 'ubuntu-advantage'):
            assert app in model.applications

        haproxy_app = model.applications['haproxy']
        trusted = await haproxy_app.get_trusted()
        assert trusted is True


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_channels_revs(event_loop):
    pytest.skip('Revise to use local charms - shouldnt fail b/c of origin')
    async with base.CleanModel() as model:
        charm = 'cs:~johnsca/libjuju-test'
        stable = await model.deploy(charm, 'a1')
        edge = await model.deploy(charm, 'a2', channel='edge')
        rev = await model.deploy(charm + '-2', 'a3')

        assert [a.charm_url for a in (stable, edge, rev)] == [
            'cs:~johnsca/libjuju-test-1',
            'cs:~johnsca/libjuju-test-2',
            'cs:~johnsca/libjuju-test-2',
        ]


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_from_ch_with_series(event_loop):
    charm = 'ch:ubuntu'
    for series in ['focal']:
        async with base.CleanModel() as model:
            app_name = "ubuntu-{}".format(series)
            await model.deploy(charm, application_name=app_name, series=series)
            status = (await model.get_status())
            app_status = status["applications"][app_name]

            if 'series' in app_status.serialize():
                s = app_status['series']
            else:
                # If there's no series, we should have a base
                s = base_channel_to_series(app_status.base.channel)
            assert s == series


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_from_ch_with_invalid_series(event_loop):
    async with base.CleanModel() as model:
        charm = 'ch:ubuntu'
        try:
            await model.deploy(charm, series='invalid')
            assert False, 'Invalid deployment should raise JujuError'
        except JujuError:
            pass


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_machine(event_loop):
    from juju.machine import Machine

    async with base.CleanModel() as model:
        # add a new default machine
        machine1 = await model.add_machine()

        # add a machine with constraints, disks, and series
        machine2 = await model.add_machine(
            constraints={
                'arch': 'amd64',
                'mem': 256 * MB,
            },
            disks=[{
                'size': 10 * GB,
                'count': 1,
            }],
            series='xenial',
        )

        # add a lxd container to machine2
        machine3 = await model.add_machine(
            'lxd:{}'.format(machine2.id))

        for m in (machine1, machine2, machine3):
            assert isinstance(m, Machine)

        assert len(model.machines) == 3

        await machine3.destroy(force=True)
        await machine2.destroy(force=True)
        res = await machine1.destroy(force=True)

        assert res is None
        assert len(model.machines) == 0


async def add_manual_machine_ssh(event_loop, is_root=False):

    # Verify controller is localhost
    async with base.CleanController() as controller:
        cloud = await controller.get_cloud()
        if cloud != "localhost":
            pytest.skip('Skipping because test requires lxd.')

    async with base.CleanModel() as model:
        private_key_path = os.path.expanduser(
            "~/.local/share/juju/ssh/juju_id_rsa"
        )
        public_key_path = os.path.expanduser(
            "~/.local/share/juju/ssh/juju_id_rsa.pub"
        )

        # connect using the local unix socket
        client = pylxd.Client()

        test_name = "test-{}-add-manual-machine-ssh".format(
            uuid.uuid4().hex[-4:]
        )

        if is_root:
            test_user = "root"
        else:
            # Create a randomized user name
            test_user = ''.join(random.choice(string.ascii_lowercase) for i in range(10))

        # create profile w/cloud-init and juju ssh key
        public_key = ""
        with open(public_key_path, "r") as f:
            public_key = f.readline()

        cloud_init = """
        #cloud-config
        users:
        - name: {}
          ssh_pwauth: False
          ssh_authorized_keys:
            - {}
          sudo: ["ALL=(ALL) NOPASSWD:ALL"]
          groups: adm, sudoers
        """.format(test_user, public_key)

        if is_root:
            cloud_init = """
            #cloud-config
            users:
            - name: {}
              ssh_authorized_keys:
                - {}
            """.format(test_user, public_key)

        profile = client.profiles.create(
            test_name,
            config={'user.user-data': cloud_init},
            devices={
                'root': {'path': '/', 'pool': 'default', 'type': 'disk'},
                'eth0': {
                    'nictype': 'bridged',
                    'parent': 'lxdbr0',
                    'type': 'nic'
                }
            }
        )

        # create lxc machine
        config = {
            'name': test_name,
            'source': {
                'type': 'image',
                'alias': 'focal',
                'mode': 'pull',
                'protocol': 'simplestreams',
                'server': 'https://cloud-images.ubuntu.com/releases',
            },
            'profiles': [test_name],
        }
        container = client.containers.create(config, wait=True)
        container.start(wait=True)

        def wait_for_network(container, timeout=30):
            """Wait for eth0 to have an ipv4 address."""
            starttime = time.perf_counter()
            while time.perf_counter() < starttime + timeout:
                time.sleep(1)
                if 'eth0' in container.state().network:
                    addresses = container.state().network['eth0']['addresses']
                    if len(addresses) > 0:
                        if addresses[0]['family'] == 'inet':
                            return addresses[0]
            return None

        host = wait_for_network(container)
        assert host, 'Failed to get address for machine'

        # HACK: We need to give sshd a chance to bind to the interface,
        # and pylxd's container.execute seems to be broken and fails and/or
        # hangs trying to properly check if the service is up.
        time.sleep(5)
        spec = 'ssh:{}@{}:{}'.format(
            test_user,
            host['address'],
            private_key_path,
        )
        err = None
        for attempt in range(1, 4):
            try:
                # add a new manual machine
                machine1 = await model.add_machine(spec=spec)
            except (paramiko.ssh_exception.NoValidConnectionsError, paramiko.ssh_exception.AuthenticationException) as e:
                # retry the ssh connection a few times if it fails
                err = e
                time.sleep(attempt * 5)
            else:
                # try part finished without exception, breaking
                break

        if len(model.machines) != 1:
            container.stop(wait=True)
            container.delete(wait=True)
            profile.delete()
            raise AssertionError('Unable to add_machine in %s attempts with spec : %s -- exception was %s' % (attempt, spec, err))

        res = await machine1.destroy(force=True)

        if res is not None:
            container.stop(wait=True)
            container.delete(wait=True)
            profile.delete()
            raise AssertionError('Bad teardown, res is : %s' % res)

        if len(model.machines) != 0:
            container.stop(wait=True)
            container.delete(wait=True)
            profile.delete()
            raise AssertionError('Unable to destroy the added machine during cleanup -- model has : %s machines' % len(model.machines))

        container.stop(wait=True)
        container.delete(wait=True)
        profile.delete()


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_manual_machine_ssh(event_loop):
    """Test manual machine provisioning with a non-root user

    Tests manual machine provisioning using a randomized username with sudo access.
    """
    await add_manual_machine_ssh(event_loop, is_root=False)


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_manual_machine_ssh_root(event_loop):
    """Test manual machine provisioning with the root user"""

    await add_manual_machine_ssh(event_loop, is_root=True)


@base.bootstrapped
@pytest.mark.asyncio
async def test_relate(event_loop):
    from juju.relation import Relation

    async with base.CleanModel() as model:
        await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='bionic',
            channel='stable',
        )
        await model.deploy(
            'nrpe',
            application_name='nrpe',
            series='bionic',
            channel='stable',
            # subordinates must be deployed without units
            num_units=0,
        )

        relation_added = jasyncio.Event()
        timeout = jasyncio.Event()

        class TestObserver(ModelObserver):
            async def on_relation_add(self, delta, old, new, model):
                if set(new.key.split()) == {'nrpe:general-info',
                                            'ubuntu:juju-info'}:
                    relation_added.set()
                    event_loop.call_later(10, timeout.set)

        model.add_observer(TestObserver())

        real_app_facade = client.ApplicationFacade.from_connection(model.connection())
        mock_app_facade = mock.MagicMock()

        async def mock_AddRelation(*args, **kwargs):
            # force response delay from AddRelation to test race condition
            # (see https://github.com/juju/python-libjuju/issues/191)
            result = await real_app_facade.AddRelation(*args, **kwargs)
            await relation_added.wait()
            return result

        mock_app_facade.AddRelation = mock_AddRelation

        with mock.patch.object(client.ApplicationFacade, 'from_connection',
                               return_value=mock_app_facade):
            my_relation = await run_with_interrupt(model.relate(
                'ubuntu',
                'nrpe',
            ), timeout)

        assert isinstance(my_relation, Relation)


async def _deploy_in_loop(new_loop, model_name, jujudata):
    new_model = Model(jujudata=jujudata)
    await new_model.connect(model_name)
    try:
        await new_model.deploy('ubuntu', channel='stable')
        assert 'ubuntu' in new_model.applications
    finally:
        await new_model.disconnect()


@base.bootstrapped
@pytest.mark.asyncio
async def test_explicit_loop_threaded(event_loop):
    async with base.CleanModel() as model:
        model_name = model.name
        new_loop = jasyncio.new_event_loop()
        with ThreadPoolExecutor(1) as executor:
            f = executor.submit(
                new_loop.run_until_complete,
                _deploy_in_loop(new_loop,
                                model_name,
                                model._connector.jujudata))
            f.result()
        await model._wait_for_new('application', 'ubuntu')
        assert 'ubuntu' in model.applications


@base.bootstrapped
@pytest.mark.asyncio
async def test_store_resources_charm(event_loop):
    pytest.skip('Revise: test_store_resources_charm intermittent test failure')
    async with base.CleanModel() as model:
        ghost = await model.deploy('ghost', channel='stable')
        assert 'ghost' in model.applications
        terminal_statuses = ('active', 'error', 'blocked')
        await model.block_until(
            lambda: (
                len(ghost.units) > 0 and
                ghost.units[0].workload_status in terminal_statuses),
            timeout=60 * 4
        )
        # ghost will go in to blocked (or error, for older
        # charm revs) if the resource is missing
        assert ghost.units[0].workload_status == 'active'


@base.bootstrapped
@pytest.mark.asyncio
async def test_local_oci_image_resource_charm(event_loop):
    charm_path = TESTS_DIR / 'integration' / 'oci-image-charm'
    async with base.CleanModel() as model:
        resources = {"oci-image": "ubuntu/latest"}
        charm = await model.deploy(str(charm_path), resources=resources)
        assert 'oci-image-charm' in model.applications
        terminal_statuses = ('active', 'error', 'blocked')
        await model.block_until(
            lambda: (
                len(charm.units) > 0 and
                charm.units[0].workload_status in terminal_statuses),
            timeout=60 * 10,
        )
        assert charm.units[0].workload_status == 'active'


@base.bootstrapped
@pytest.mark.asyncio
async def test_local_file_resource_charm(event_loop):
    charm_path = TESTS_DIR / 'integration' / 'file-resource-charm'
    async with base.CleanModel() as model:
        resources = {"file-res": "test.file"}
        app = await model.deploy(str(charm_path), resources=resources)
        assert 'file-resource-charm' in model.applications

        await model.wait_for_idle()
        assert app.units[0].agent_status == 'idle'

        ress = await app.get_resources()
        assert 'file-res' in ress
        assert ress['file-res']


@base.bootstrapped
@pytest.mark.asyncio
async def test_attach_resource(event_loop):
    charm_path = TESTS_DIR / 'integration' / 'file-resource-charm'
    async with base.CleanModel() as model:
        resources = {"file-res": "test.file"}
        app = await model.deploy(str(charm_path), resources=resources)
        assert 'file-resource-charm' in model.applications

        await model.wait_for_idle()
        assert app.units[0].agent_status == 'idle'

        with open(str(charm_path / 'test.file')) as f:
            app.attach_resource('file-res', 'test.file', f)

        with open(str(charm_path / 'test.file'), 'rb') as f:
            app.attach_resource('file-res', 'test.file', f)


@base.bootstrapped
@pytest.mark.asyncio
async def test_store_resources_bundle(event_loop):
    pytest.skip('test_store_resources_bundle intermittent test failure')
    async with base.CleanModel() as model:
        bundle = str(Path(__file__).parent / 'bundle')
        await model.deploy(bundle)
        assert 'ghost' in model.applications
        ghost = model.applications['ghost']
        terminal_statuses = ('active', 'error', 'blocked')
        await model.block_until(
            lambda: (
                len(ghost.units) > 0 and
                ghost.units[0].workload_status in terminal_statuses)
        )
        # ghost will go in to blocked (or error, for older
        # charm revs) if the resource is missing
        assert ghost.units[0].workload_status == 'active'
        resources = await ghost.get_resources()
        assert resources['ghost-stable'].revision >= 12


@base.bootstrapped
@pytest.mark.asyncio
async def test_store_resources_bundle_revs(event_loop):
    pytest.skip('test_store_resources_bundle_revs intermittent test failure')
    async with base.CleanModel() as model:
        bundle = str(Path(__file__).parent / 'bundle/bundle-resource-rev.yaml')
        await model.deploy(bundle)
        assert 'ghost' in model.applications
        ghost = model.applications['ghost']
        terminal_statuses = ('active', 'error', 'blocked')
        await model.block_until(
            lambda: (
                len(ghost.units) > 0 and
                ghost.units[0].workload_status in terminal_statuses)
        )
        # ghost will go in to blocked (or error, for older
        # charm revs) if the resource is missing
        assert ghost.units[0].workload_status == 'active'
        resources = await ghost.get_resources()
        assert resources['ghost-stable'].revision == 11


@base.bootstrapped
@pytest.mark.asyncio
async def test_ssh_key(event_loop):
    async with base.CleanModel() as model:
        await model.add_ssh_key('admin', SSH_KEY)
        result = await model.get_ssh_key(True)
        result = result.serialize()['results'][0].serialize()['result']
        assert SSH_KEY in result
        await model.remove_ssh_key('admin', SSH_KEY)
        result = await model.get_ssh_key(True)
        result = result.serialize()['results'][0].serialize()['result']
        assert result is None


@base.bootstrapped
@pytest.mark.asyncio
async def test_get_machines(event_loop):
    async with base.CleanModel() as model:
        result = await model.get_machines()
        assert isinstance(result, list)


@base.bootstrapped
@pytest.mark.asyncio
async def test_wait_for_idle_without_units(event_loop):
    async with base.CleanModel() as model:
        await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='bionic',
            channel='stable',
            num_units=0,
        )
        with pytest.raises(jasyncio.TimeoutError):
            await model.wait_for_idle(timeout=10)


@base.bootstrapped
@pytest.mark.asyncio
async def test_wait_for_idle_with_not_enough_units(event_loop):
    async with base.CleanModel() as model:
        await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='bionic',
            channel='stable',
            num_units=2,
        )
        with pytest.raises(jasyncio.TimeoutError):
            await model.wait_for_idle(timeout=5 * 60, wait_for_units=3)


@base.bootstrapped
@pytest.mark.asyncio
async def test_wait_for_idle_with_enough_units(event_loop):
    async with base.CleanModel() as model:
        await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='bionic',
            channel='stable',
            num_units=3,
        )
        await model.wait_for_idle(timeout=5 * 60, wait_for_units=3)


@base.bootstrapped
@pytest.mark.asyncio
async def test_wait_for_idle_with_exact_units(event_loop):
    async with base.CleanModel() as model:
        await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='bionic',
            channel='stable',
            num_units=2,
        )
        await model.wait_for_idle(timeout=5 * 60, wait_for_exact_units=2)


@base.bootstrapped
@pytest.mark.asyncio
async def test_wait_for_idle_with_exact_units_scale_down(event_loop):
    """Deploys 3 units, waits for them to be idle, then removes 2 of them,
    then waits for exactly 1 unit to be left.

    """
    async with base.CleanModel() as model:
        app = await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='bionic',
            channel='stable',
            num_units=3,
        )
        await model.wait_for_idle(timeout=5 * 60, wait_for_exact_units=3)

        two_units_to_remove = [u.name for u in app.units[:2]]
        await app.destroy_units(*two_units_to_remove)

        # assert that the following wait is not returning instantaneously
        start_time = time.perf_counter()
        await model.wait_for_idle(timeout=5 * 60, wait_for_exact_units=1)
        end_time = time.perf_counter()
        # checking if waited more than 10ms
        assert (end_time - start_time) > 0.001


@base.bootstrapped
@pytest.mark.asyncio
async def test_wait_for_idle_with_exact_units_scale_down_zero(event_loop):
    """Deploys 3 units, waits for them to be idle, then removes 3 of them,
    then waits for exactly 0 unit to be left.

    """
    async with base.CleanModel() as model:
        app = await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='bionic',
            channel='stable',
            num_units=3,
        )
        await model.wait_for_idle(timeout=5 * 60, wait_for_exact_units=3)

        units_to_remove = [u.name for u in app.units]
        # Remove all the units
        await app.destroy_units(*units_to_remove)

        # assert that the following wait is not returning instantaneously
        start_time = time.perf_counter()
        await model.wait_for_idle(timeout=5 * 60, wait_for_exact_units=0)
        end_time = time.perf_counter()
        # checking if waited more than 10ms
        assert (end_time - start_time) > 0.001


@base.bootstrapped
@pytest.mark.asyncio
async def test_watcher_reconnect(event_loop):
    async with base.CleanModel() as model:
        await model.connection().close()
        await block_until(model.is_connected, timeout=3)


@base.bootstrapped
@pytest.mark.asyncio
async def test_config(event_loop):
    async with base.CleanModel() as model:
        # first test get_config with nothing.
        result = await model.get_config()
        assert 'extra-info' not in result
        await model.set_config({
            'extra-info': 'booyah',
            'test-mode': client.ConfigValue(value=True),
        })
        result = await model.get_config()
        assert 'extra-info' in result
        assert result['extra-info'].source == 'model'
        assert result['extra-info'].value == 'booyah'


@base.bootstrapped
@pytest.mark.asyncio
async def test_config_with_json(event_loop):
    async with base.CleanModel() as model:
        # first test get_config with nothing.
        result = await model.get_config()
        assert 'extra-complex-info' not in result
        # test model config with more complex data
        expected = ['foo', {'bar': 1}]
        await model.set_config({
            'extra-complex-info': json.dumps(expected),
            'test-mode': client.ConfigValue(value=True),
        })
        result = await model.get_config()
        assert 'extra-complex-info' in result
        assert result['extra-complex-info'].source == 'model'
        recieved = json.loads(result['extra-complex-info'].value)
        assert recieved == recieved


@base.bootstrapped
@pytest.mark.asyncio
async def test_set_constraints(event_loop):
    async with base.CleanModel() as model:
        await model.set_constraints({'cpu-power': 1})
        cons = await model.get_constraints()
        assert cons['cpu_power'] == 1

# @base.bootstrapped
# @pytest.mark.asyncio
# async def test_grant(event_loop)
#    async with base.CleanController() as controller:
#        await controller.add_user('test-model-grant')
#        await controller.grant('test-model-grant', 'superuser')
#    async with base.CleanModel() as model:
#        await model.grant('test-model-grant', 'admin')
#        assert model.get_user('test-model-grant')['access'] == 'admin'
#        await model.grant('test-model-grant', 'login')
#        assert model.get_user('test-model-grant')['access'] == 'login'


@base.bootstrapped
@pytest.mark.asyncio
async def test_model_annotations(event_loop):

    async with base.CleanModel() as model:
        annotations = await model.get_annotations()
        assert len(annotations) == 0

        expected = {"foo": "bar", "another": "value"}
        await model.set_annotations(expected)

        annotations = await model.get_annotations()
        assert annotations == expected


@base.bootstrapped
@pytest.mark.asyncio
async def test_machine_annotations(event_loop):

    async with base.CleanModel() as model:
        machine = await model.add_machine()

        annotations = await machine.get_annotations()
        assert len(annotations) == 0

        expected = {"foo": "bar", "another": "value"}
        await machine.set_annotations(expected)

        annotations = await machine.get_annotations()
        assert annotations == expected


@base.bootstrapped
@pytest.mark.asyncio
async def test_application_annotations(event_loop):

    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu', channel="stable")

        annotations = await app.get_annotations()
        assert len(annotations) == 0

        expected = {"foo": "bar", "another": "value"}
        await app.set_annotations(expected)

        annotations = await app.get_annotations()
        assert annotations == expected


@base.bootstrapped
@pytest.mark.asyncio
async def test_unit_annotations(event_loop):

    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu', channel="stable")
        await model.wait_for_idle()
        unit = app.units[0]

        annotations = await unit.get_annotations()
        assert len(annotations) == 0

        expected = {"foo": "bar", "another": "value"}
        await unit.set_annotations(expected)

        annotations = await unit.get_annotations()
        assert annotations == expected


@base.bootstrapped
@pytest.mark.asyncio
async def test_backups(event_loop):
    pytest.skip('Revise: mongodb issues')
    m = Model()
    await m.connect(model_name='controller')
    test_start = await m.get_backups()
    num_of_backups_before_test = len(test_start)

    # Create a backup
    local_file_name, extra_info = await m.create_backup(notes="hi")
    assert 'id' in extra_info
    assert 'checksum' in extra_info

    assert extra_info['notes'] == "hi"

    # Check if the file is downloaded on disk
    assert os.path.exists(local_file_name)

    test_over = await m.get_backups()
    assert len(test_over) == num_of_backups_before_test

    # Cleanup
    os.remove(local_file_name)
    await m.disconnect()


@base.bootstrapped
@pytest.mark.asyncio
async def test_connect_to_connection(event_loop):
    async with base.CleanModel() as test_model:
        # get the connection from test_model
        conn = test_model.connection()

        # make a new Model obj
        m = Model()

        # it's not connected yet
        assert not m.is_connected()

        # connect it directly to the connection
        await m.connect_to(conn)

        # it is connected
        assert m.is_connected()

        # cleanup
        await m.disconnect()


@base.bootstrapped
@pytest.mark.asyncio
@pytest.skip("This assumes that we have a model to connect to...")
async def test_connect_current(event_loop):
    m = Model()
    await m.connect_current()
    assert m.is_connected()


@base.bootstrapped
@pytest.mark.asyncio
async def test_model_cache_update(event_loop):
    """Connecting to a new model shouldn't fail because the cache is not
    updated yet

    """
    async with base.CleanController() as controller:
        await controller.connect_current()

        model_name = "new-test-model"
        m = await controller.add_model(model_name)

        model_uuids = await controller.model_uuids()
        assert model_name in model_uuids

        model = Model()

        try:
            await model.connect(model_name=model_name)
        except JujuConnectionError:
            # avoid leaking the model if the test fails
            await model.disconnect()
            await m.disconnect()
            await controller.destroy_models(model_name)
            raise

        # cleanup
        await model.disconnect()
        await m.disconnect()
        await controller.destroy_models(model_name)


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_storage(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('postgresql')
        await model.wait_for_idle(status="active")
        unit = app.units[0]
        ret = await unit.add_storage("pgdata")
        assert any([tag.storage("pgdata") in s for s in ret])


@base.bootstrapped
@pytest.mark.asyncio
async def test_model_attach_storage_at_deploy(event_loop):
    pytest.skip('detach/attach_storage inconsistent on Juju side, unable to test')
    async with base.CleanModel() as model:
        # The attach_storage needs to be an existing storage,
        # so the plan is to:
        # - Deploy postgresql
        # - Create and attach a storage
        # - Detach storage
        # - Remove app
        # - Re-deploy with attach_storage parameter
        # - Make sure the storage is there
        app = await model.deploy('postgresql')
        await model.wait_for_idle(status="active")

        unit = app.units[0]
        ret = await unit.add_storage("pgdata")
        assert any([tag.storage("pgdata") in s for s in ret])
        storage_id = ret[0]

        await unit.detach_storage(storage_id, force=True)
        await jasyncio.sleep(10)

        storages1 = await model.list_storage()
        assert any([storage_id in s['storage-tag'] for s in storages1])

        # juju remove-application
        # actually removes the storage even though the destroy_storage=false
        await app.destroy(destroy_storage=False)
        await jasyncio.sleep(10)

        storages2 = await model.list_storage()
        assert any([storage_id in s['storage-tag'] for s in storages2])

        await model.deploy('postgresql', attach_storage=[storage_id])
        await model.wait_for_idle(status="active")

        storages3 = await model.list_storage()
        assert any([storage_id in s['storage-tag'] for s in storages3])


@base.bootstrapped
@pytest.mark.asyncio
async def test_detach_storage(event_loop):
    pytest.skip('detach/attach_storage inconsistent on Juju side, unable to test')
    async with base.CleanModel() as model:
        app = await model.deploy('postgresql')
        await model.wait_for_idle(status="active")
        unit = app.units[0]
        storage_ids = await unit.add_storage("pgdata")
        storage_id = storage_ids[0]
        await jasyncio.sleep(5)

        _storage_details_1 = await model.show_storage_details(storage_id)
        storage_details_1 = _storage_details_1[0]
        assert 'unit-postgresql-0' in storage_details_1['attachments']

        await unit.detach_storage(storage_id, force=True)
        await jasyncio.sleep(20)

        _storage_details_2 = await model.show_storage_details(storage_id)
        storage_details_2 = _storage_details_2[0]
        assert ('unit-postgresql-0' not in storage_details_2['attachments']) or \
            storage_details_2['attachments']['unit-postgresql-0'].life == 'dying'

        # remove_storage
        await model.remove_storage(storage_id, force=True)
        await jasyncio.sleep(10)
        storages = await model.list_storage()
        assert all([storage_id not in s['storage-tag'] for s in storages])


@base.bootstrapped
@pytest.mark.asyncio
async def test_list_storage(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('postgresql')
        await model.wait_for_idle(status="active")
        unit = app.units[0]
        await unit.add_storage("pgdata")
        storages = await model.list_storage()
        await model.list_storage(filesystem=True)
        await model.list_storage(volume=True)

        assert any([tag.storage("pgdata") in s['storage-tag'] for s in storages])


@base.bootstrapped
@pytest.mark.asyncio
async def test_storage_pools(event_loop):
    async with base.CleanModel() as model:
        await model.deploy('postgresql')
        await model.wait_for_idle(status="active")

        await model.create_storage_pool("test-pool", "lxd")
        pools = await model.list_storage_pools()
        assert "test-pool" in [p['name'] for p in pools]

        await model.remove_storage_pool("test-pool")
        await jasyncio.sleep(5)
        pools = await model.list_storage_pools()
        assert "test-pool" not in [p['name'] for p in pools]
