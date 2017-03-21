import asyncio
from concurrent.futures import ThreadPoolExecutor
import pytest

from .. import base
from juju.controller import Controller
from juju.errors import JujuAPIError


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_user(event_loop):
    async with base.CleanController() as controller:
        await controller.add_user('test')
        result = await controller.get_user('test')
        res_ser = result.serialize()['results'][0].serialize()
        assert res_ser['result'] is not None


@base.bootstrapped
@pytest.mark.asyncio
async def test_disable_enable_user(event_loop):
    async with base.CleanController() as controller:
        await controller.add_user('test-disable')
        await controller.disable_user('test-disable')
        result = await controller.get_user('test-disable')
        res_ser = result.serialize()['results'][0].serialize()
        assert res_ser['result'].serialize()['disabled'] is True
        await controller.enable_user('test-disable')
        result = await controller.get_user('test-disable')
        res_ser = result.serialize()['results'][0].serialize()
        assert res_ser['result'].serialize()['disabled'] is False


@base.bootstrapped
@pytest.mark.asyncio
async def test_change_user_password(event_loop):
    async with base.CleanController() as controller:
        await controller.add_user('test-password')
        await controller.change_user_password('test-password', 'password')
        try:
            con = await controller.connect(controller.connection.endpoint, 'test-password', 'password')
            result = True
        except JujuAPIError:
            result = False
        assert result is True


@base.bootstrapped
@pytest.mark.asyncio
async def test_grant(event_loop):
    async with base.CleanController() as controller:
        await controller.add_user('test-grant')
        await controller.grant('test-grant', 'superuser')
        result = await controller.get_user('test-grant')
        result = result.serialize()['results'][0].serialize()['result'].serialize()
        assert result['access'] == 'superuser'
        await controller.grant('test-grant', 'login')
        result = await controller.get_user('test-grant')
        result = result.serialize()['results'][0].serialize()['result'].serialize()
        assert result['access'] == 'login'
