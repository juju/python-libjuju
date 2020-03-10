import asyncio
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
from juju.client.client import ApplicationFacade, ConfigValue
from juju.errors import JujuError
from juju.model import Model, ModelObserver
from juju.utils import block_until, run_with_interrupt

from .. import base

MB = 1
GB = 1024
SSH_KEY = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsYMJGNGG74HAJha3n2CFmWYsOOaORnJK6VqNy86pj0MIpvRXBzFzVy09uPQ66GOQhTEoJHEqE77VMui7+62AcMXT+GG7cFHcnU8XVQsGM6UirCcNyWNysfiEMoAdZScJf/GvoY87tMEszhZIUV37z8PUBx6twIqMdr31W1J0IaPa+sV6FEDadeLaNTvancDcHK1zuKsL39jzAg7+LYjKJfEfrsQP+lj/EQcjtKqlhVS5kzsJVfx8ZEd0xhW5G7N6bCdKNalS8mKCMaBXJpijNQ82AiyqCIDCRrre2To0/i7pTjRiL0U9f9mV3S4NJaQaokR050w/ZLySFf6F7joJT mathijs@Qrama-Mathijs'  # noqa


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_bundle_dir(event_loop):
    tests_dir = Path(__file__).absolute().parent.parent
    bundle_path = tests_dir / 'bundle'

    async with base.CleanModel() as model:
        await model.deploy(str(bundle_path))

        wordpress = model.applications.get('wordpress')
        mysql = model.applications.get('mysql')
        assert wordpress and mysql
        await block_until(lambda: (len(wordpress.units) == 1 and
                                   len(mysql.units) == 1),
                          timeout=60 * 4)


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_bundle_file(event_loop):
    tests_dir = Path(__file__).absolute().parent.parent
    bundle_path = tests_dir / 'bundle'
    mini_bundle_file_path = bundle_path / 'mini-bundle.yaml'

    async with base.CleanModel() as model:
        await model.deploy(str(mini_bundle_file_path))

        dummy_sink = model.applications.get('dummy-sink')
        dummy_subordinate = model.applications.get('dummy-subordinate')
        assert dummy_sink and dummy_subordinate
        await block_until(lambda: (len(dummy_sink.units) == 1 and
                                   len(dummy_subordinate.units) == 1),
                          timeout=60 * 4)


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_invalid_bundle(event_loop):
    pytest.skip('test_deploy_invalid_bundle intermittent test failure')
    tests_dir = Path(__file__).absolute().parent.parent
    bundle_path = tests_dir / 'bundle' / 'invalid.yaml'
    async with base.CleanModel() as model:
        with pytest.raises(JujuError):
            await model.deploy(str(bundle_path))


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_charm(event_loop):
    from pathlib import Path
    tests_dir = Path(__file__).absolute().parent.parent
    charm_path = tests_dir / 'charm'

    async with base.CleanModel() as model:
        await model.deploy(str(charm_path))
        assert 'charm' in model.applications


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_bundle(event_loop):
    async with base.CleanModel() as model:
        await model.deploy('bundle/wiki-simple')

        for app in ('wiki', 'mysql'):
            assert app in model.applications


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_charm_folder_symlink(event_loop):
    from pathlib import Path
    tests_dir = Path(__file__).absolute().parent.parent
    charm_path = tests_dir / 'charm-folder-symlink'

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
        await model.deploy('cs:~juju-qa/bundle/basic-trusted-1', trust=True)

        for app in ('ubuntu', 'ubuntu-lite'):
            assert app in model.applications

        ubuntu_app = model.applications['ubuntu']
        trusted = await ubuntu_app.get_trusted()
        assert trusted is True


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_channels_revs(event_loop):
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
                'pool': 'rootfs',
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


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_manual_machine_ssh(event_loop):
    """Test manual machine provisioning with a non-root user

    Tests manual machine provisioning using a randomized username with sudo access.
    """

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
                'alias': 'xenial',
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
            starttime = time.time()
            while(time.time() < starttime + timeout):
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

        for attempt in range(1, 4):
            try:
                # add a new manual machine
                machine1 = await model.add_machine(spec='ssh:{}@{}:{}'.format(
                    test_user,
                    host['address'],
                    private_key_path,
                ))
            except paramiko.ssh_exception.NoValidConnectionsError:
                # retry the ssh connection a few times if it fails
                time.sleep(attempt * 5)
            else:
                break

            assert len(model.machines) == 1

            res = await machine1.destroy(force=True)

            assert res is None
            assert len(model.machines) == 0

        container.stop(wait=True)
        container.delete(wait=True)

        profile.delete()


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_manual_machine_ssh_root(event_loop):
    """Test manual machine provisioning with the root user"""

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

        # create profile w/cloud-init and juju ssh key
        public_key = ""
        with open(public_key_path, "r") as f:
            public_key = f.readline()

        cloud_init = """
        #cloud-config
        users:
        - name: root
          ssh_authorized_keys:
            - {}
        """.format(public_key)

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
                'alias': 'xenial',
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
            starttime = time.time()
            while(time.time() < starttime + timeout):
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

        for attempt in range(1, 4):
            try:
                # add a new manual machine
                machine1 = await model.add_machine(spec='ssh:{}@{}:{}'.format(
                    "root",
                    host['address'],
                    private_key_path,
                ))
            except (paramiko.ssh_exception.NoValidConnectionsError, paramiko.ssh_exception.AuthenticationException):
                time.sleep(attempt * 5)
            else:
                break

        assert len(model.machines) == 1

        res = await machine1.destroy(force=True)

        assert res is None
        assert len(model.machines) == 0

        container.stop(wait=True)
        container.delete(wait=True)

        profile.delete()


@base.bootstrapped
@pytest.mark.asyncio
async def test_relate(event_loop):
    from juju.relation import Relation

    async with base.CleanModel() as model:
        await model.deploy(
            'cs:~jameinel/ubuntu-lite-7',
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

        relation_added = asyncio.Event()
        timeout = asyncio.Event()

        class TestObserver(ModelObserver):
            async def on_relation_add(self, delta, old, new, model):
                if set(new.key.split()) == {'nrpe:general-info',
                                            'ubuntu:juju-info'}:
                    relation_added.set()
                    event_loop.call_later(10, timeout.set)

        model.add_observer(TestObserver())

        real_app_facade = ApplicationFacade.from_connection(model.connection())
        mock_app_facade = mock.MagicMock()

        async def mock_AddRelation(*args, **kwargs):
            # force response delay from AddRelation to test race condition
            # (see https://github.com/juju/python-libjuju/issues/191)
            result = await real_app_facade.AddRelation(*args, **kwargs)
            await relation_added.wait()
            return result

        mock_app_facade.AddRelation = mock_AddRelation

        with mock.patch.object(ApplicationFacade, 'from_connection',
                               return_value=mock_app_facade):
            my_relation = await run_with_interrupt(model.add_relation(
                'ubuntu',
                'nrpe',
            ), timeout, loop=event_loop)

        assert isinstance(my_relation, Relation)


async def _deploy_in_loop(new_loop, model_name, jujudata):
    new_model = Model(new_loop, jujudata=jujudata)
    await new_model.connect(model_name)
    try:
        await new_model.deploy('cs:xenial/ubuntu')
        assert 'ubuntu' in new_model.applications
    finally:
        await new_model.disconnect()


@base.bootstrapped
@pytest.mark.asyncio
async def test_explicit_loop_threaded(event_loop):
    async with base.CleanModel() as model:
        model_name = model.info.name
        new_loop = asyncio.new_event_loop()
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
    pytest.skip('test_store_resources_charm intermittent test failure')
    async with base.CleanModel() as model:
        ghost = await model.deploy('cs:ghost-19')
        assert 'ghost' in model.applications
        terminal_statuses = ('active', 'error', 'blocked')
        await model.block_until(
            lambda: (
                len(ghost.units) > 0 and
                ghost.units[0].workload_status in terminal_statuses)
        )
        # ghost will go in to blocked (or error, for older
        # charm revs) if the resource is missing
        assert ghost.units[0].workload_status == 'active'


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
async def test_watcher_reconnect(event_loop):
    async with base.CleanModel() as model:
        await model.connection().ws.close()
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
            'test-mode': ConfigValue(value=True),
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
            'test-mode': ConfigValue(value=True),
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
        app = await model.deploy('ubuntu')

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
        app = await model.deploy('ubuntu')
        unit = app.units[0]

        annotations = await unit.get_annotations()
        assert len(annotations) == 0

        expected = {"foo": "bar", "another": "value"}
        await unit.set_annotations(expected)

        annotations = await unit.get_annotations()
        assert annotations == expected
