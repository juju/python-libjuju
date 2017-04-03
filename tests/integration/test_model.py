import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pytest

from .. import base
from juju.model import Model

MB = 1
GB = 1024


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


@base.bootstrapped
@pytest.mark.asyncio
async def test_store_resources_charm(event_loop):
    async with base.CleanModel() as model:
        ghost = await model.deploy('cs:ghost-18')
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
