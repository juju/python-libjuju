from juju.client import client

import pytest

from .. import base


@base.bootstrapped
@pytest.mark.asyncio
async def test_user_info(event_loop):
    async with base.CleanModel() as model:
        controller_conn = await model.connection().controller()

        um = client.UserManagerFacade.from_connection(controller_conn)
        result = await um.UserInfo(
            entities=[client.Entity('user-admin')], include_disabled=True)
        await controller_conn.close()

        assert isinstance(result, client.UserInfoResults)
        for r in result.results:
            assert isinstance(r, client.UserInfoResult)
