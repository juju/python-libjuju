import asyncio

import pytest

from .. import base

MB = 1


@base.bootstrapped
@pytest.mark.asyncio
async def test_action(event_loop):
    async with base.CleanModel() as model:
        ubuntu_app = await model.deploy(
            'percona-cluster',
            application_name='mysql',
            series='xenial',
            channel='stable',
            config={
                'tuning-level': 'safest',
            },
            constraints={
                'arch': 'amd64',
                'mem': 256 * MB,
            },
        )

        # update and check app config
        await ubuntu_app.set_config({'tuning-level': 'fast'})
        config = await ubuntu_app.get_config()
        assert config['tuning-level']['value'] == 'fast'

        # Restore config back to default
        await ubuntu_app.reset_config(['tuning-level'])
        config = await ubuntu_app.get_config()
        assert config['tuning-level']['value'] == 'safest'

        # update and check app constraints
        await ubuntu_app.set_constraints({'mem': 512 * MB})
        constraints = await ubuntu_app.get_constraints()
        assert constraints['mem'] == 512 * MB

        # check action definitions
        actions = await ubuntu_app.get_actions()
        assert 'backup' in actions.keys()


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
        await model.block_until(lambda: (len(app.units) > 0 and
                                         app.units[0].machine))
        assert app.data['charm-url'] == 'cs:ubuntu-0'
        await app.upgrade_charm()
        assert app.data['charm-url'].startswith('cs:ubuntu-')
        assert app.data['charm-url'] != 'cs:ubuntu-0'


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm_channel(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu-0')
        await model.block_until(lambda: (len(app.units) > 0 and
                                         app.units[0].machine))
        assert app.data['charm-url'] == 'cs:ubuntu-0'
        await app.upgrade_charm(channel='stable')
        assert app.data['charm-url'].startswith('cs:ubuntu-')
        assert app.data['charm-url'] != 'cs:ubuntu-0'


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm_revision(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu-0')
        await model.block_until(lambda: (len(app.units) > 0 and
                                         app.units[0].machine))
        assert app.data['charm-url'] == 'cs:ubuntu-0'
        await app.upgrade_charm(revision=8)
        assert app.data['charm-url'] == 'cs:ubuntu-8'


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm_switch(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu-0')
        await model.block_until(lambda: (len(app.units) > 0 and
                                         app.units[0].machine))
        assert app.data['charm-url'] == 'cs:ubuntu-0'
        await app.upgrade_charm(switch='ubuntu-8')
        assert app.data['charm-url'] == 'cs:ubuntu-8'


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm_resource(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('cs:~juju-qa/bionic/upgrade-charm-resource-test-0')

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

        await app.upgrade_charm(revision=1)
        await asyncio.wait_for(
            model.block_until(
                lambda: unit.workload_status_message != 'I have no resource.'
            ),
            timeout=60
        )
        expected_message = 'My resource: I am the resource.'
        assert app.units[0].workload_status_message == expected_message


@base.bootstrapped
@pytest.mark.asyncio
async def test_trusted(event_loop):
    async with base.CleanModel() as model:
        await model.deploy('cs:~juju-qa/bundle/basic-trusted-1', trust=True)

        ubuntu_app = model.applications['ubuntu']
        trusted = await ubuntu_app.get_trusted()
        assert trusted is True

        await ubuntu_app.set_trusted(False)
        trusted = await ubuntu_app.get_trusted()
        assert trusted is False
