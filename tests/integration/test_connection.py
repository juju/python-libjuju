import asyncio

from juju.client import client
from juju.client.connection import Connection

import pytest

from .. import base


@base.bootstrapped
@pytest.mark.asyncio
async def test_monitor(event_loop):

    async with base.CleanModel() as model:
        conn = model.connection()
        assert conn.monitor.status == 'connected'
        await conn.close()

        assert conn.monitor.status == 'disconnected'


@base.bootstrapped
@pytest.mark.asyncio
async def test_monitor_catches_error(event_loop):

    async with base.CleanModel() as model:
        conn = model.connection()

        assert conn.monitor.status == 'connected'
        try:
            async with conn.monitor.reconnecting:
                await conn.ws.close()
                await asyncio.sleep(1)
                assert conn.monitor.status == 'error'
        finally:
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

        c = client.ClientFacade.from_connection(model.connection())

        await c.FullStatus(None)


@base.bootstrapped
@pytest.mark.asyncio
async def test_reconnect(event_loop):
    async with base.CleanModel() as model:
        kwargs = model.connection().connect_params()
        conn = await Connection.connect(**kwargs)
        try:
            await asyncio.sleep(0.1)
            assert conn.is_open
            await conn.ws.close()
            assert not conn.is_open
            await model.block_until(lambda: conn.is_open, timeout=3)
        finally:
            await conn.close()
