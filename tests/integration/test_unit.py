import pytest

from .. import base


@base.bootstrapped
@pytest.mark.asyncio
async def test_run(event_loop):
    from juju.action import Action

    async with base.CleanModel() as model:
        app = await model.deploy(
            'ubuntu-0',
            application_name='ubuntu',
            series='trusty',
            channel='stable',
        )

        for unit in app.units:
            action = await unit.run('unit-get public-address')
            assert isinstance(action, Action)
            assert 'Stdout' in action.results
            break


@base.bootstrapped
@pytest.mark.asyncio
async def test_run_action(event_loop):
    async def run_action(unit):
        # unit.run() returns a juju.action.Action instance
        action = await unit.run_action('add-repo', repo='myrepo')
        # wait for the action to complete
        return await action.wait()

    async with base.CleanModel() as model:
        app = await model.deploy(
            'git',
            application_name='git',
            series='trusty',
            channel='stable',
        )

        for unit in app.units:
            action = await run_action(unit)
            assert action.results == {'dir': '/var/git/myrepo.git'}
            break
