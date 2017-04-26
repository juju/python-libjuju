import pytest
import uuid

from .. import base
from juju.controller import Controller
from juju.errors import JujuAPIError


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_user(event_loop):
    async with base.CleanController() as controller:
        username = 'test{}'.format(uuid.uuid4())
        await controller.add_user(username)
        result = await controller.get_user(username)
        res_ser = result.serialize()['results'][0].serialize()
        assert res_ser['result'] is not None


@base.bootstrapped
@pytest.mark.asyncio
async def test_disable_enable_user(event_loop):
    async with base.CleanController() as controller:
        username = 'test-disable{}'.format(uuid.uuid4())
        await controller.add_user(username)
        await controller.disable_user(username)
        result = await controller.get_user(username)
        res_ser = result.serialize()['results'][0].serialize()
        assert res_ser['result'].serialize()['disabled'] is True
        await controller.enable_user(username)
        result = await controller.get_user(username)
        res_ser = result.serialize()['results'][0].serialize()
        assert res_ser['result'].serialize()['disabled'] is False


@base.bootstrapped
@pytest.mark.asyncio
async def test_change_user_password(event_loop):
    async with base.CleanController() as controller:
        username = 'test-password{}'.format(uuid.uuid4())
        await controller.add_user(username)
        await controller.change_user_password(username, 'password')
        try:
            new_controller = Controller()
            await new_controller.connect(
                controller.connection.endpoint, username, 'password')
            result = True
            await new_controller.disconnect()
        except JujuAPIError:
            result = False
        assert result is True


@base.bootstrapped
@pytest.mark.asyncio
async def test_grant(event_loop):
    async with base.CleanController() as controller:
        username = 'test-grant{}'.format(uuid.uuid4())
        await controller.add_user(username)
        await controller.grant(username, 'superuser')
        result = await controller.get_user(username)
        result = result.serialize()['results'][0].serialize()['result']\
            .serialize()
        assert result['access'] == 'superuser'
        await controller.grant(username, 'login')
        result = await controller.get_user(username)
        result = result.serialize()['results'][0].serialize()['result']\
            .serialize()
        assert result['access'] == 'login'


@base.bootstrapped
@pytest.mark.asyncio
async def test_get_models(event_loop):
    async with base.CleanController() as controller:
        result = await controller.get_models()
        assert isinstance(result.serialize()['user-models'], list)
