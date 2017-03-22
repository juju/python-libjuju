import asyncio
from concurrent.futures import ThreadPoolExecutor
import pytest

from .. import base
from juju.model import Model

MB = 1
GB = 1024
SSH_KEY = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsYMJGNGG74HAJha3n2CFmWYsOOaORnJK6VqNy86pj0MIpvRXBzFzVy09uPQ66GOQhTEoJHEqE77VMui7+62AcMXT+GG7cFHcnU8XVQsGM6UirCcNyWNysfiEMoAdZScJf/GvoY87tMEszhZIUV37z8PUBx6twIqMdr31W1J0IaPa+sV6FEDadeLaNTvancDcHK1zuKsL39jzAg7+LYjKJfEfrsQP+lj/EQcjtKqlhVS5kzsJVfx8ZEd0xhW5G7N6bCdKNalS8mKCMaBXJpijNQ82AiyqCIDCRrre2To0/i7pTjRiL0U9f9mV3S4NJaQaokR050w/ZLySFf6F7joJT mathijs@Qrama-Mathijs'

@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_local_bundle(event_loop):
    from pathlib import Path
    tests_dir = Path(__file__).absolute().parent.parent
    bundle_path = tests_dir / 'bundle'

    async with base.CleanModel() as model:
        await model.deploy(str(bundle_path))

        for app in ('wordpress', 'mysql'):
            assert app in model.applications


@base.bootstrapped
@pytest.mark.asyncio
async def test_deploy_bundle(event_loop):
    async with base.CleanModel() as model:
        await model.deploy('bundle/wiki-simple')

        for app in ('wiki', 'mysql'):
            assert app in model.applications


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
        my_relation = await model.add_relation(
            'ubuntu',
            'nrpe',
        )

        assert isinstance(my_relation, Relation)


async def _deploy_in_loop(new_loop, model_name):
    new_model = Model(new_loop)
    await new_model.connect_model(model_name)
    try:
        await new_model.deploy('cs:xenial/ubuntu')
        assert 'ubuntu' in new_model.applications
    finally:
        await new_model.disconnect()


@base.bootstrapped
@pytest.mark.asyncio
async def test_explicit_loop(event_loop):
    async with base.CleanModel() as model:
        model_name = model.info.name
        new_loop = asyncio.new_event_loop()
        new_loop.run_until_complete(
            _deploy_in_loop(new_loop, model_name))
        await model._wait_for_new('application', 'ubuntu')
        assert 'ubuntu' in model.applications
        await model.disconnect()


@base.bootstrapped
@pytest.mark.asyncio
async def test_explicit_loop_threaded(event_loop):
    async with base.CleanModel() as model:
        model_name = model.info.name
        new_loop = asyncio.new_event_loop()
        with ThreadPoolExecutor(1) as executor:
            f = executor.submit(
                new_loop.run_until_complete,
                _deploy_in_loop(new_loop, model_name))
            f.result()
        await model._wait_for_new('application', 'ubuntu')
        assert 'ubuntu' in model.applications
        await model.disconnect()


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
        await model.disconnect()


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
