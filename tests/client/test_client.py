import pytest

from juju.client.connection import Connection
from juju.client import client

from ..base import bootstrapped


@bootstrapped
@pytest.mark.asyncio
async def test_user_info(event_loop):
    conn = await Connection.connect_current()
    controller_conn = await conn.controller()

    um = client.UserManagerFacade()
    um.connect(controller_conn)
    result = await um.UserInfo(
        [client.Entity('user-admin')], True)
    await conn.close()
    await controller_conn.close()

    assert isinstance(result, client.UserInfoResults)
    for r in result.results:
        assert isinstance(r, client.UserInfoResult)
