# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import asyncio
from pathlib import Path
from tempfile import NamedTemporaryFile
import pytest

from juju import utils

from .. import base


@base.bootstrapped
async def test_block_coroutine(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='jammy',
            channel='stable',
            num_units=3,
        )

        async def is_leader_elected():
            return any([await u.is_leader_from_status() for u in app.units])

        await utils.block_until_with_coroutine(is_leader_elected,
                                               timeout=480,
                                               wait_period=5)


@base.bootstrapped
async def test_unit_public_address(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='jammy',
            channel='stable',
            num_units=1,
        )

        # wait for the units to come up
        await model.block_until(lambda: app.units, timeout=480)

        # make sure we have some units to test with
        assert len(app.units) >= 1
        unit = app.units[0]

        await asyncio.wait_for(
            model.block_until(lambda: unit.machine),
            timeout=60)
        machine = unit.machine
        await asyncio.wait_for(
            model.block_until(lambda: (machine.status == 'running' and
                                       machine.agent_status == 'started')),
            timeout=480)

        for unit in app.units:
            addr = await unit.get_public_address()
            assert addr is not None


@base.bootstrapped
async def test_run(event_loop):
    from juju.action import Action

    async with base.CleanModel() as model:
        app = await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='jammy',
            channel='stable',
        )

        await model.wait_for_idle(status="active")

        for unit in app.units:
            action1 = await unit.run('unit-get public-address')
            assert isinstance(action1, Action)
            assert action1.status == 'pending'
            await action1.wait()
            assert action1.status == 'completed'
            break

        for unit in app.units:
            action2 = await unit.run('sleep 3', timeout=1)
            assert isinstance(action2, Action)
            await action2.wait()
            assert action2.status == 'failed'
            break

        for unit in app.units:
            action3 = await unit.run('sleep 1', timeout=3)
            assert isinstance(action3, Action)
            await action3.wait()
            assert action3.status == 'completed'
            break

        unit = app.units[0]
        action4 = await unit.run("df -h", timeout=None)
        assert action4.status == 'pending'
        action5 = await action4.wait()
        assert action4 is action5
        assert action5.status == 'completed'
        assert action5.results
        assert action5.results['return-code'] == 0


@base.bootstrapped
async def test_run_action(event_loop):
    pytest.skip('Find a better charm for this test')

    async def run_action(unit):
        # unit.run() returns a juju.action.Action instance
        action = await unit.run_action('add-repo', repo='myrepo')
        # wait for the action to complete
        return await action.wait()

    def check_results(results, out):
        assert 'dir' in results
        assert 'stdout' in results or 'Stdout' in results
        assert 'Code' in results or 'return-code' in results
        if 'Code' in results:
            assert results['Code'] == 0
        else:
            assert results['return-code'] == 0

        if 'stdout' in results:
            assert results['stdout'] == out
        else:
            assert results['Stdout'] == out
        assert results['dir'] == '/var/git/myrepo.git'

    async with base.CleanModel() as model:
        app = await model.deploy(
            'git',
            application_name='git',
            series='trusty',
            channel='stable',
        )

        for unit in app.units:
            action = await run_action(unit)
            out = "Adding group `myrepo' (GID 1001) ...\n" \
                  'Done.\n' \
                  'Initialized empty Git repository in ' \
                  '/var/git/myrepo.git/\n'
            check_results(action.results, out)
            output = await model.get_action_output(action.entity_id, wait=5)
            check_results(output, out)
            status = await model.get_action_status(
                uuid_or_prefix=action.entity_id)
            assert status[action.entity_id] == 'completed'
            break


@base.bootstrapped
async def test_scp(event_loop):
    # ensure that asyncio.subprocess will work;
    try:
        asyncio.get_child_watcher().attach_loop(event_loop)
    except RuntimeError:
        pytest.skip('test_scp will always fail outside of MainThread')
    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu', channel='stable')

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
async def test_ssh(event_loop):
    # ensure that asyncio.subprocess will work;
    try:
        asyncio.get_child_watcher().attach_loop(event_loop)
    except RuntimeError:
        pytest.skip('test_ssh will always fail outside of MainThread')
    async with base.CleanModel() as model:
        app = await model.deploy('ubuntu', channel='stable')

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
        assert 'test' in output


@base.bootstrapped
async def test_resolve_local(event_loop):
    charm_file = Path(__file__).absolute().parent / 'charm.charm'

    async with base.CleanModel() as model:
        app = await model.deploy(
            str(charm_file),
            config={'status': 'error'},
        )

        try:
            await model.wait_for_idle(raise_on_error=False, idle_period=1)
            assert app.units[0].workload_status == 'error'

            await app.units[0].resolved()

            await model.wait_for_idle(raise_on_error=False)
            assert app.units[0].workload_status == 'active'
        finally:
            # Errored units won't get cleaned up unless we force them.
            await asyncio.gather(*(machine.destroy(force=True)
                                   for machine in model.machines.values()))


@base.bootstrapped
async def test_unit_introspect(event_loop):
    async with base.CleanModel() as model:
        await model.deploy('ubuntu', series='jammy')
        await model.wait_for_idle(status="active")

        await model.deploy('juju-introspect',
                           channel='edge',
                           series='jammy',
                           to='0',
                           )


@base.bootstrapped
async def test_subordinate_units(event_loop):
    async with base.CleanModel() as model:
        u_app = await model.deploy('ubuntu')
        n_app = await model.deploy('ntp')
        await model.relate('ubuntu', 'ntp')
        await model.wait_for_idle()

        # model subordinates
        model_subs = model.subordinate_units
        assert len(model_subs) == 1
        assert 'ntp/0' in model_subs
        assert 'ubuntu/0' not in model_subs

        n_unit = model_subs['ntp/0']
        u_unit = u_app.units[0]

        # application subordinates
        app_sub_names = [u.name for u in n_app.subordinate_units]
        assert n_unit.name in app_sub_names
        assert u_unit.name not in app_sub_names

        assert n_unit.is_subordinate
        assert not u_unit.is_subordinate
        assert n_unit.principal_unit == 'ubuntu/0'
        assert u_unit.principal_unit == ''
        assert [u.name for u in u_unit.get_subordinates()] == [n_unit.name]


@base.bootstrapped
async def test_destroy_unit(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy(
            'juju-qa-test',
            application_name='test',
            num_units=3,
        )
        # wait for the units to come up
        await model.block_until(lambda: app.units, timeout=480)

        await app.units[0].destroy()
        await asyncio.sleep(5)
        assert len(app.units) == 2
