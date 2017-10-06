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
async def test_get_models(event_loop):
    async with base.CleanController() as controller:
        result = await controller.get_models()
        assert isinstance(result.serialize()['user-models'], list)
