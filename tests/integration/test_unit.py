import asyncio
from tempfile import NamedTemporaryFile

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

        for unit in app.units:
            action = await unit.run('sleep 1', timeout=0.5)
            assert isinstance(action, Action)
            assert action.status == 'failed'
            break

        for unit in app.units:
            action = await unit.run('sleep 0.5', timeout=2)
            assert isinstance(action, Action)
            assert action.status == 'completed'
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
            assert action.results == {
                'Code': '0',
                'Stdout': "Adding group `myrepo' (GID 1001) ...\n"
                          'Done.\n'
                          'Initialized empty Git repository in '
                          '/var/git/myrepo.git/\n',
                'dir': '/var/git/myrepo.git',
            }
            out = await model.get_action_output(action.entity_id, wait=5)
            assert out == {
                'Code': '0',
                'Stdout': "Adding group `myrepo' (GID 1001) ...\n"
                          'Done.\n'
                          'Initialized empty Git repository in '
                          '/var/git/myrepo.git/\n',
                'dir': '/var/git/myrepo.git',
            }
            status = await model.get_action_status(
                uuid_or_prefix=action.entity_id)
            assert status[action.entity_id] == 'completed'
            break


@base.bootstrapped
@pytest.mark.asyncio
async def test_scp(event_loop):
    # ensure that asyncio.subprocess will work;
    try:
        asyncio.get_child_watcher().attach_loop(event_loop)
    except RuntimeError:
        pytest.skip('test_scp will always fail outside of MainThread')
    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu')

        await asyncio.wait_for(
            model.block_until(lambda: app.units),
            timeout=60)
        unit = app.units[0]
        await asyncio.wait_for(
            model.block_until(lambda: unit.machine),
            timeout=60)
        machine = unit.machine
        await asyncio.wait_for(
            model.block_until(lambda: (machine.status == 'running' and
                                       machine.agent_status == 'started')),
            timeout=480)

        with NamedTemporaryFile() as f:
            f.write(b'testcontents')
            f.flush()
            await unit.scp_to(f.name, 'testfile')

        with NamedTemporaryFile() as f:
            await unit.scp_from('testfile', f.name)
            assert f.read() == b'testcontents'


@base.bootstrapped
@pytest.mark.asyncio
async def test_ssh(event_loop):
    # ensure that asyncio.subprocess will work;
    try:
        asyncio.get_child_watcher().attach_loop(event_loop)
    except RuntimeError:
        pytest.skip('test_ssh will always fail outside of MainThread')
    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu')

        await asyncio.wait_for(
            model.block_until(lambda: app.units),
            timeout=60)
        unit = app.units[0]
        await asyncio.wait_for(
            model.block_until(lambda: unit.machine),
            timeout=60)
        machine = unit.machine
        await asyncio.wait_for(
            model.block_until(lambda: (machine.status == 'running' and
                                       machine.agent_status == 'started')),
            timeout=480)
        output = await unit.ssh("echo test")
        assert(output == "test")


@base.bootstrapped
@pytest.mark.asyncio
async def test_resolve(event_loop):

    async with base.CleanModel() as model:
        app = await model.deploy(
            'ubuntu-0',
            application_name='ubuntu',
            series='trusty',
            channel='stable',
        )

        # Resolving a hook not in an error state is not a great test but at
        # least it exercises the code.
        for unit in app.units:
            await unit.resolved()
