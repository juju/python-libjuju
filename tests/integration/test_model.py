import asyncio
import mock
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from juju.client.client import ConfigValue, ApplicationFacade
from juju.model import Model, ModelObserver
from juju.utils import block_until, run_with_interrupt

import pytest

from .. import base


MB = 1
GB = 1024
SSH_KEY = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsYMJGNGG74HAJha3n2CFmWYsOOaORnJK6VqNy86pj0MIpvRXBzFzVy09uPQ66GOQhTEoJHEqE77VMui7+62AcMXT+GG7cFHcnU8XVQsGM6UirCcNyWNysfiEMoAdZScJf/GvoY87tMEszhZIUV37z8PUBx6twIqMdr31W1J0IaPa+sV6FEDadeLaNTvancDcHK1zuKsL39jzAg7+LYjKJfEfrsQP+lj/EQcjtKqlhVS5kzsJVfx8ZEd0xhW5G7N6bCdKNalS8mKCMaBXJpijNQ82AiyqCIDCRrre2To0/i7pTjRiL0U9f9mV3S4NJaQaokR050w/ZLySFf6F7joJT mathijs@Qrama-Mathijs'  # noqa


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_bundle(event_loop):
    from pathlib import Path
    tests_dir = Path(__file__).absolute().parent.parent
    bundle_path = tests_dir / 'bundle'
    mini_bundle_file_path = bundle_path / 'mini-bundle.yaml'

    async with base.CleanModel() as model:
        await model.deploy(str(bundle_path))
        await model.deploy(str(mini_bundle_file_path))

        for app in ('wordpress', 'mysql', 'myapp'):
            assert app in model.applications


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
async def test_relate(event_loop):
    from juju.relation import Relation

    async with base.CleanModel() as model:
        await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='trusty',
            channel='stable',
        )
        await model.deploy(
            'nrpe',
            application_name='nrpe',
            series='trusty',
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
                    event_loop.call_later(2, timeout.set)

        model.add_observer(TestObserver())

        real_app_facade = ApplicationFacade.from_connection(model.connection())
        mock_app_facade = mock.MagicMock()

        async def mock_AddRelation(*args):
            # force response delay from AddRelation to test race condition
            # (see https://github.com/juju/python-libjuju/issues/191)
            result = await real_app_facade.AddRelation(*args)
            await relation_added.wait()
            return result

        mock_app_facade.AddRelation = mock_AddRelation

        with mock.patch.object(ApplicationFacade, 'from_connection',
                               return_value=mock_app_facade):
            my_relation = await run_with_interrupt(model.add_relation(
                'ubuntu',
                'nrpe',
            ), timeout, event_loop)

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
                _deploy_in_loop(new_loop, model_name, model._connector.jujudata))
            f.result()
        await model._wait_for_new('application', 'ubuntu')
        assert 'ubuntu' in model.applications


@base.bootstrapped
@pytest.mark.asyncio
async def test_store_resources_charm(event_loop):
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
        await model.set_config({
            'extra-info': 'booyah',
            'test-mode': ConfigValue(value=True),
        })
        result = await model.get_config()
        assert 'extra-info' in result
        assert result['extra-info'].source == 'model'
        assert result['extra-info'].value == 'booyah'

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
