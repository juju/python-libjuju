import asyncio
import subprocess
import uuid

from juju.client.connection import Connection
from juju.client import client
from juju.client.jujudata import FileJujuData
from juju.controller import Controller
from juju.errors import JujuAPIError

import pytest

from .. import base


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_remove_user(event_loop):
    async with base.CleanController() as controller:
        username = 'test{}'.format(uuid.uuid4())
        user = await controller.get_user(username)
        assert user is None
        user = await controller.add_user(username)
        assert user is not None
        assert user.secret_key is not None
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
        # Check that we can connect with the new password.
        new_connection = None
        try:
            kwargs = controller.connection().connect_params()
            kwargs['username'] = username
            kwargs['password'] = 'password'
            new_connection = await Connection.connect(**kwargs)
        except JujuAPIError:
            raise AssertionError('Unable to connect with new password')
        finally:
            if new_connection:
                await new_connection.close()


@base.bootstrapped
@pytest.mark.asyncio
async def test_reset_user_password(event_loop):
    async with base.CleanController() as controller:
        username = 'test{}'.format(uuid.uuid4())
        user = await controller.add_user(username)
        origin_secret_key = user.secret_key
        await user.set_password('password')
        await controller.reset_user_password(username)
        user = await controller.get_user(username)
        new_secret_key = user.secret_key
        # Check secret key is different after the reset.
        assert origin_secret_key != new_secret_key
        # Check that we can't connect with the old password.
        new_connection = None
        try:
            kwargs = controller.connection().connect_params()
            kwargs['username'] = username
            kwargs['password'] = 'password'
            new_connection = await Connection.connect(**kwargs)
        except JujuAPIError:
            pass
        finally:
            # No connection with old password
            assert new_connection is None


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
        await user.grant('login')  # already has 'superuser', so no-op
        assert user.access == 'superuser'
        fresh = await controller.get_user(username)  # fetch fresh copy
        assert fresh.access == 'superuser'
        await user.revoke()
        assert user.access == ''
        fresh = await controller.get_user(username)  # fetch fresh copy
        assert fresh.access == ''


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


async def _wait_for_model(controller, model_name):
    while model_name not in await controller.list_models():
        await asyncio.sleep(0.5, loop=controller.loop)


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
        await asyncio.wait_for(_wait_for_model(controller,
                                               model_name),
                               timeout=60)
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
        await asyncio.wait_for(_wait_for_model(controller,
                                               model_name),
                               timeout=60)
        await controller.destroy_model(model_uuid)
        await asyncio.wait_for(_wait_for_model_gone(controller,
                                                    model_name),
                               timeout=60)


# this test must be run serially because it modifies the login password
@pytest.mark.serial
@base.bootstrapped
@pytest.mark.asyncio
async def test_macaroon_auth(event_loop):
    jujudata = FileJujuData()
    account = jujudata.accounts()[jujudata.current_controller()]
    with base.patch_file('~/.local/share/juju/accounts.yaml'):
        if 'password' in account:
            # force macaroon auth by "changing" password to current password
            result = subprocess.run(
                ['juju', 'change-user-password'],
                input='{0}\n{0}\n'.format(account['password']),
                universal_newlines=True,
                stderr=subprocess.PIPE)
            assert result.returncode == 0, ('Failed to change password: '
                                            '{}'.format(result.stderr))
        controller = Controller()
        try:
            await controller.connect()
            assert controller.is_connected()
        finally:
            if controller.is_connected():
                await controller.disconnect()
        async with base.CleanModel():
            pass  # create and login to model works


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_remove_cloud(event_loop):
    async with base.CleanController() as controller:
        cloud_name = 'test-{}'.format(uuid.uuid4())
        cloud = client.Cloud(
            auth_types=["userpass"],
            endpoint="http://localhost:1234",
            type_="kubernetes")
        cloud = await controller.add_cloud(cloud_name, cloud)
        try:
            assert cloud.auth_types[0] == "userpass"
            assert cloud.endpoint == "http://localhost:1234"
            assert cloud.type_ == "kubernetes"
        finally:
            await controller.remove_cloud(cloud_name)
