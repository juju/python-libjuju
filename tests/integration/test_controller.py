import asyncio
import pytest
import uuid

from .. import base
from juju.controller import Controller
from juju.errors import JujuAPIError


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_remove_user(event_loop):
    async with base.CleanController() as controller:
        username = 'test{}'.format(uuid.uuid4())
        user = await controller.get_user(username)
        assert user is None
        user = await controller.add_user(username)
        assert user is not None
        assert user.username == username
        users = await controller.get_users()
        assert any(u.username == username for u in users)
        await controller.remove_user(username)
        user = await controller.get_user(username)
        assert user is None
        users = await controller.get_users()
        assert not any(u.username == username for u in users)


@base.bootstrapped
@pytest.mark.asyncio
async def test_disable_enable_user(event_loop):
    async with base.CleanController() as controller:
        username = 'test-disable{}'.format(uuid.uuid4())
        user = await controller.add_user(username)

        await user.disable()
        assert not user.enabled
        assert user.disabled

        fresh = await controller.get_user(username)  # fetch fresh copy
        assert not fresh.enabled
        assert fresh.disabled

        await user.enable()
        assert user.enabled
        assert not user.disabled

        fresh = await controller.get_user(username)  # fetch fresh copy
        assert fresh.enabled
        assert not fresh.disabled


@base.bootstrapped
@pytest.mark.asyncio
async def test_change_user_password(event_loop):
    async with base.CleanController() as controller:
        username = 'test-password{}'.format(uuid.uuid4())
        user = await controller.add_user(username)
        await user.set_password('password')
        try:
            new_controller = Controller()
            await new_controller.connect(
                controller.connection.endpoint, username, 'password')
        except JujuAPIError:
            raise AssertionError('Unable to connect with new password')
        finally:
            await new_controller.disconnect()


@base.bootstrapped
@pytest.mark.asyncio
async def test_grant_revoke(event_loop):
    async with base.CleanController() as controller:
        username = 'test-grant{}'.format(uuid.uuid4())
        user = await controller.add_user(username)
        await user.grant('superuser')
        assert user.access == 'superuser'
        fresh = await controller.get_user(username)  # fetch fresh copy
        assert fresh.access == 'superuser'
        await user.grant('login')
        assert user.access == 'login'
        fresh = await controller.get_user(username)  # fetch fresh copy
        assert fresh.access == 'login'
        await user.revoke()
        assert user.access is ''
        fresh = await controller.get_user(username)  # fetch fresh copy
        assert fresh.access is ''


@base.bootstrapped
@pytest.mark.asyncio
async def test_list_models(event_loop):
    async with base.CleanController() as controller:
        async with base.CleanModel() as model:
            result = await controller.list_models()
            assert model.info.name in result


@base.bootstrapped
@pytest.mark.asyncio
async def test_get_model(event_loop):
    async with base.CleanController() as controller:
        by_name, by_uuid = None, None
        model_name = 'test-{}'.format(uuid.uuid4())
        model = await controller.add_model(model_name)
        model_uuid = model.info.uuid
        await model.disconnect()
        try:
            by_name = await controller.get_model(model_name)
            by_uuid = await controller.get_model(model_uuid)
            assert by_name.info.name == model_name
            assert by_name.info.uuid == model_uuid
            assert by_uuid.info.name == model_name
            assert by_uuid.info.uuid == model_uuid
        finally:
            if by_name:
                await by_name.disconnect()
            if by_uuid:
                await by_uuid.disconnect()
            await controller.destroy_model(model_name)


async def _wait_for_model_gone(controller, model_name):
    while model_name in await controller.list_models():
        await asyncio.sleep(0.5, loop=controller.loop)


@base.bootstrapped
@pytest.mark.asyncio
async def test_destroy_model_by_name(event_loop):
    async with base.CleanController() as controller:
        model_name = 'test-{}'.format(uuid.uuid4())
        model = await controller.add_model(model_name)
        await model.disconnect()
        await controller.destroy_model(model_name)
        await asyncio.wait_for(_wait_for_model_gone(controller,
                                                    model_name),
                               timeout=60)


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_destroy_model_by_uuid(event_loop):
    async with base.CleanController() as controller:
        model_name = 'test-{}'.format(uuid.uuid4())
        model = await controller.add_model(model_name)
        model_uuid = model.info.uuid
        await model.disconnect()
        await controller.destroy_model(model_uuid)
        await asyncio.wait_for(_wait_for_model_gone(controller,
                                                    model_name),
                               timeout=60)
