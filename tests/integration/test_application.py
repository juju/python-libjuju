from pathlib import Path

import pytest
import logging

from .. import base
from juju import errors
from juju.url import URL, Schema

MB = 1

logger = logging.getLogger(__name__)


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
async def test_get_set_config(event_loop):
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

        config = await ubuntu_app.get_config()
        await ubuntu_app.set_config(config)

        config2 = await ubuntu_app.get_config()
        assert config == config2


@base.bootstrapped
@pytest.mark.asyncio
async def test_status_is_not_unset(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy(
            'cs:ubuntu-0',
            application_name='ubuntu',
            series='trusty',
            channel='stable',
        )

        assert app.status != 'unset'


@base.bootstrapped
@pytest.mark.asyncio
async def test_status(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('cs:~juju-qa/blocked-0')

        def app_ready():
            if not app.units:
                return False
            return app.status == 'blocked'

        await model.block_until(app_ready, timeout=480)
        assert app.status == 'blocked'


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_units(event_loop):
    from juju.unit import Unit

    async with base.CleanModel() as model:
        app = await model.deploy(
            'cs:ubuntu-0',
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
async def test_deploy_charmhub_charm(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('ch:hello-juju')
        await model.block_until(lambda: (len(app.units) > 0 and
                                         app.units[0].machine))
        assert 'hello-juju' in app.data['charm-url']


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('cs:ubuntu-0')
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
        app = await model.deploy('cs:ubuntu-0')
        await model.block_until(lambda: (len(app.units) > 0 and
                                         app.units[0].machine))
        assert app.data['charm-url'] == 'cs:ubuntu-0'
        await app.upgrade_charm(channel='stable')
        assert app.data['charm-url'].startswith('cs:ubuntu-')
        assert app.data['charm-url'] != 'cs:ubuntu-0'


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm_switch_channel(event_loop):
    # Note for future:
    # This test requires a charm that has different
    # revisions for different channels/risks.
    # Currently, we use juju-qa-test, but eventually
    # (when the 'edge' moves to 'stable') this test
    # will be testing nothing (if not failing).
    # So checks are in place for that.

    async with base.CleanModel() as model:
        app = await model.deploy('juju-qa-test', channel='2.0/stable')
        await model.wait_for_idle(status='active')

        charm_url = URL.parse(app.data['charm-url'])
        assert Schema.CHARM_HUB.matches(charm_url.schema)
        still22 = False
        try:
            assert charm_url.revision == 22
            still22 = True
        except AssertionError:
            logger.warning("Charm used in test_upgrade_charm_switch_channel "
                           "seems to have been updated, the test needs to be revised")

        await app.upgrade_charm(channel='2.0/edge')
        await model.wait_for_idle(status='active')

        if still22:
            try:
                charm_url = URL.parse(app.data['charm-url'])
                assert charm_url.revision == 23
            except AssertionError:
                raise errors.JujuError("Either the upgrade has failed, or the used charm moved "
                                       "the candidate channel to stable, so no upgrade took place, "
                                       "the test needs to be revised.")

        # Try with another charm too, just in case, no need to check revisions etc
        app = await model.deploy('ubuntu', channel='stable')
        await model.wait_for_idle(status='active')
        await app.upgrade_charm(channel='candidate')
        await model.wait_for_idle(status='active')


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm_revision(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('cs:ubuntu-0')
        await model.block_until(lambda: (len(app.units) > 0 and
                                         app.units[0].machine))
        assert app.data['charm-url'] == 'cs:ubuntu-0'
        await app.upgrade_charm(revision=8)
        assert app.data['charm-url'] == 'cs:ubuntu-8'


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm_switch(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('cs:ubuntu-0')
        await model.block_until(lambda: (len(app.units) > 0 and
                                         app.units[0].machine))
        assert app.data['charm-url'] == 'cs:ubuntu-0'
        with pytest.raises(errors.JujuError):
            await app.upgrade_charm(switch='ubuntu-8')
        await app.upgrade_charm(switch='cs:ubuntu-8')
        assert app.data['charm-url'] == 'cs:ubuntu-8'


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_local_charm(event_loop):
    async with base.CleanModel() as model:
        tests_dir = Path(__file__).absolute().parent
        charm_path = tests_dir / 'upgrade-charm'
        app = await model.deploy('ch:ubuntu', series='focal')
        await model.wait_for_idle(status="active")
        assert app.data['charm-url'].startswith('ch:') and 'ubuntu' in \
               app.data['charm-url']
        await app.upgrade_charm(path=charm_path)
        await model.wait_for_idle(status="waiting")
        assert app.data['charm-url'] == 'local:focal/ubuntu-0'


@base.bootstrapped
@pytest.mark.asyncio
async def test_upgrade_charm_resource(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('cs:~juju-qa/bionic/upgrade-charm-resource-test-0')

        await model.wait_for_idle(wait_for_units=1)
        unit = app.units[0]
        expected_message = 'I have no resource.'
        assert unit.workload_status_message == expected_message

        await app.upgrade_charm(revision=1)
        await model.block_until(
            lambda: unit.workload_status_message != 'I have no resource.',
            timeout=60,
        )
        expected_message = 'My resource: I am the resource.'
        assert app.units[0].workload_status_message == expected_message


@base.bootstrapped
@pytest.mark.asyncio
async def test_trusted(event_loop):
    async with base.CleanModel() as model:
        await model.deploy('ubuntu', trust=True)

        ubuntu_app = model.applications['ubuntu']
        trusted = await ubuntu_app.get_trusted()
        assert trusted is True

        await ubuntu_app.set_trusted(False)
        trusted = await ubuntu_app.get_trusted()
        assert trusted is False


@base.bootstrapped
@pytest.mark.asyncio
async def test_app_remove_wait_flag(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu')
        a_name = app.name
        await model.wait_for_idle(status="active")

        await model.remove_application(app.name, block_until_done=True)
        assert a_name not in model.applications
