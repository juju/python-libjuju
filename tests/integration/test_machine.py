import asyncio
from tempfile import NamedTemporaryFile

import pytest

from .. import base


@base.bootstrapped
@pytest.mark.asyncio
async def test_status(event_loop):
    async with base.CleanModel() as model:
        await model.deploy(
            'ubuntu-0',
            application_name='ubuntu',
            series='trusty',
            channel='stable',
        )

        await asyncio.wait_for(
            model.block_until(lambda: len(model.machines)),
            timeout=240)
        machine = model.machines['0']

        assert machine.status in ('allocating', 'pending')
        assert machine.agent_status == 'pending'
        assert not machine.agent_version

        # there is some inconsistency in the capitalization of status_message
        # between different providers
        await asyncio.wait_for(
            model.block_until(
                lambda: (machine.status == 'running' and
                         machine.status_message.lower() == 'running' and
                         machine.agent_status == 'started')),
            timeout=480)


@base.bootstrapped
@pytest.mark.asyncio
async def test_scp(event_loop):
    # ensure that asyncio.subprocess will work;
    try:
        asyncio.get_child_watcher().attach_loop(event_loop)
    except RuntimeError:
        pytest.skip('test_scp will always fail outside of MainThread')
    async with base.CleanModel() as model:
        await model.add_machine()
        await asyncio.wait_for(
            model.block_until(lambda: model.machines),
            timeout=240)
        machine = model.machines['0']
        await asyncio.wait_for(
            model.block_until(lambda: (machine.status == 'running' and
                                       machine.agent_status == 'started')),
            timeout=480)

        with NamedTemporaryFile() as f:
            f.write(b'testcontents')
            f.flush()
            await machine.scp_to(f.name, 'testfile', scp_opts='-p')

        with NamedTemporaryFile() as f:
            await machine.scp_from('testfile', f.name, scp_opts='-p')
            assert f.read() == b'testcontents'
