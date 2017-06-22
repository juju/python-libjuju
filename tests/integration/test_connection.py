import asyncio
import pytest

from juju.client.connection import Connection
from juju.client import client
from .. import base


@base.bootstrapped
@pytest.mark.asyncio
async def test_connect_current(event_loop):
    async with base.CleanModel():
        conn = await Connection.connect_current()

        assert isinstance(conn, Connection)
        await conn.close()


@base.bootstrapped
@pytest.mark.asyncio
async def test_monitor(event_loop):

    async with base.CleanModel():
        conn = await Connection.connect_current()

        assert conn.monitor.status == 'connected'
        await conn.close()

        assert conn.monitor.status == 'disconnected'


@base.bootstrapped
@pytest.mark.asyncio
async def test_monitor_catches_error(event_loop):

    async with base.CleanModel():
        conn = await Connection.connect_current()

        assert conn.monitor.status == 'connected'
        await conn.ws.close()

        assert conn.monitor.status == 'error'

        await conn.close()


@base.bootstrapped
@pytest.mark.asyncio
async def test_full_status(event_loop):
    async with base.CleanModel() as model:
        await model.deploy(
            'ubuntu-0',
            application_name='ubuntu',
            series='trusty',
            channel='stable',
        )

        c = client.ClientFacade.from_connection(model.connection)

        await c.FullStatus(None)


@base.bootstrapped
@pytest.mark.asyncio
async def test_reconnect(event_loop):
    async with base.CleanModel() as model:
        conn = await Connection.connect(
            model.connection.endpoint,
            model.connection.uuid,
            model.connection.username,
            model.connection.password,
            model.connection.cacert,
            model.connection.macaroons,
            model.connection.loop,
            model.connection.max_frame_size)
        try:
            await asyncio.sleep(0.1)
            assert conn.is_open
            await conn.ws.close()
            assert not conn.is_open
            await model.block_until(lambda: conn.is_open, timeout=3)
        finally:
            await conn.close()
