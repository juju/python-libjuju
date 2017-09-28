import asyncio
import pytest

from .. import base

MB = 1


@base.bootstrapped
@pytest.mark.asyncio
async def test_action(event_loop):
    async with base.CleanModel() as model:
        ubuntu_app = await model.deploy(
            'mysql',
            application_name='mysql',
            series='trusty',
            channel='stable',
            config={
                'tuning-level': 'safest',
            },
            constraints={
                'mem': 256 * MB,
            },
        )

        # update and check app config
        await ubuntu_app.set_config({'tuning-level': 'fast'})
        config = await ubuntu_app.get_config()
        assert config['tuning-level']['value'] == 'fast'

        # update and check app constraints
        await ubuntu_app.set_constraints({'mem': 512 * MB})
        constraints = await ubuntu_app.get_constraints()
        assert constraints['mem'] == 512 * MB


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_units(event_loop):
    from juju.unit import Unit

    async with base.CleanModel() as model:
        app = await model.deploy(
            'ubuntu-0',
            application_name='ubuntu',
            series='trusty',
            channel='stable',
        )
        units = await app.add_units(count=2)

        assert len(units) == 2
        for unit in units:
            assert isinstance(unit, Unit)


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu-0')
        assert app.data['charm-url'] == 'cs:ubuntu-0'
        await app.upgrade_charm()
        assert app.data['charm-url'].startswith('cs:ubuntu-')
        assert app.data['charm-url'] != 'cs:ubuntu-0'


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm_channel(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu-0')
        assert app.data['charm-url'] == 'cs:ubuntu-0'
        await app.upgrade_charm(channel='stable')
        assert app.data['charm-url'].startswith('cs:ubuntu-')
        assert app.data['charm-url'] != 'cs:ubuntu-0'


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm_revision(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu-0')
        assert app.data['charm-url'] == 'cs:ubuntu-0'
        await app.upgrade_charm(revision=8)
        assert app.data['charm-url'] == 'cs:ubuntu-8'


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm_switch(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu-0')
        assert app.data['charm-url'] == 'cs:ubuntu-0'
        await app.upgrade_charm(switch='ubuntu-8')
        assert app.data['charm-url'] == 'cs:ubuntu-8'


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm_resource(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('cs:~cynerva/upgrade-charm-resource-test-1')

        def units_ready():
            if not app.units:
                return False
            unit = app.units[0]
            return unit.workload_status == 'active' and \
                unit.agent_status == 'idle'

        await asyncio.wait_for(model.block_until(units_ready), timeout=480)
        unit = app.units[0]
        expected_message = 'I have no resource.'
        assert unit.workload_status_message == expected_message

        await app.upgrade_charm(revision=2)
        await asyncio.wait_for(
            model.block_until(
                lambda: unit.workload_status_message != 'I have no resource.'
            ),
            timeout=60
        )
        expected_message = 'My resource: I am the resource.'
        assert app.units[0].workload_status_message == expected_message
