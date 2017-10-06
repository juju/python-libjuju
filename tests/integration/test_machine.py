import asyncio
import pytest

from tempfile import NamedTemporaryFile

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

        await asyncio.wait_for(
            model.block_until(lambda: (machine.status == 'running' and
                                       machine.agent_status == 'started' and
                                       machine.agent_version is not None)),
            timeout=480)

        assert machine.status == 'running'
        # there is some inconsistency in the message case between providers
        assert machine.status_message.lower() == 'running'
        assert machine.agent_status == 'started'
        assert machine.agent_version.major >= 2


@base.bootstrapped
@pytest.mark.asyncio
async def test_scp(event_loop):
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
            await machine.scp_to(f.name, 'testfile')

        with NamedTemporaryFile() as f:
            await machine.scp_from('testfile', f.name)
            assert f.read() == b'testcontents'
