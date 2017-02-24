import pytest

from juju.client.connection import Connection
from .. import base


@base.bootstrapped
@pytest.mark.asyncio
async def test_connect_current(event_loop):
    async with base.CleanModel():
        conn = await Connection.connect_current()

        assert isinstance(conn, Connection)
        await conn.close()
