import pytest

from juju.client.connection import Connection
from ..base import bootstrapped


@bootstrapped
@pytest.mark.asyncio
async def test_connect_current(event_loop):
    conn = await Connection.connect_current()

    assert isinstance(conn, Connection)
    await conn.close()
