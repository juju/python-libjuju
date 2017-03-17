import asyncio
from concurrent.futures import ThreadPoolExecutor
import pytest

from .. import base
from juju.controller import Controller


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
        await controller.disable_user('test2')
        result = await controller.get_user('test2')
        res_ser = result.serialize()['results'][0].serialize()
        assert res_ser['result'] is None
        await controller.enable_user('test2')
        result = await controller.get_user('test2')
        res_ser = result.serialize()['results'][0].serialize()
        assert res_ser['result'] is not None
