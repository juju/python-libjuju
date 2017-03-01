import pytest

from .. import base

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
