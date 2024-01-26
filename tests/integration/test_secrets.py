# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import pytest
from .. import base
from ..utils import TESTS_DIR
from juju.errors import JujuNotSupportedError


@base.bootstrapped
@pytest.mark.bundle
async def test_add_secret():
    async with base.CleanModel() as model:
        try:
            secret = await model.add_secret(name='my-apitoken', data_args=['token=34ae35facd4'])
            assert secret.startswith('secret:')

            secrets = await model.list_secrets()
            assert len(secrets) == 1
            assert secrets[0].label == 'my-apitoken'
        except JujuNotSupportedError:
            pass


# This test can only work if we can fully upgrade the whole charm
# with the corresponding logic :)
@base.bootstrapped
async def test_list_secrets():
    """Use the charm-secret charm definition and see if the
    arguments defined in the secret are correct or not."""

    charm_path = TESTS_DIR / 'charm-secret/charm-secret_ubuntu-22.04-amd64.charm'

    async with base.CleanModel() as model:
        await model.deploy(str(charm_path))
        assert 'charm-secret' in model.applications
        await model.wait_for_idle(status="active")
        assert model.units['charm-secret/0'].workload_status == 'active'

        try:
            secrets = await model.list_secrets(show_secrets=True)
            assert secrets is not None
            assert len(secrets) == 1
        except JujuNotSupportedError:
            pass


@base.bootstrapped
@pytest.mark.bundle
async def test_update_secret():
    async with base.CleanModel() as model:
        try:
            secret = await model.add_secret(name='my-apitoken', data_args=['token=34ae35facd4'])
            assert secret.startswith('secret:')

            await model.update_secret(name='my-apitoken', new_name='new-token')

            secrets = await model.list_secrets()
            assert len(secrets) == 1
            assert secrets[0].label == 'new-token'
        except JujuNotSupportedError:
            pass


@base.bootstrapped
@pytest.mark.bundle
async def test_remove_secret():
    async with base.CleanModel() as model:
        try:
            secret = await model.add_secret(name='my-apitoken', data_args=['token=34ae35facd4'])
            assert secret.startswith('secret:')

            await model.remove_secret('my-apitoken')

            secrets = await model.list_secrets()
            assert len(secrets) == 0
        except JujuNotSupportedError:
            pass


@base.bootstrapped
@pytest.mark.bundle
async def test_grant_secret():
    async with base.CleanModel() as model:
        try:
            secret = await model.add_secret(name='my-apitoken', data_args=['token=34ae35facd4'])
            assert secret.startswith('secret:')

            await model.deploy('ubuntu')

            await model.grant_secret('my-apitoken', 'ubuntu')
        except JujuNotSupportedError:
            pass


@base.bootstrapped
@pytest.mark.bundle
async def test_revoke_secret():
    async with base.CleanModel() as model:
        try:
            secret = await model.add_secret(name='my-apitoken', data_args=['token=34ae35facd4'])
            assert secret.startswith('secret:')
            await model.revoke_secret('my-apitoken', 'ubuntu')
        except JujuNotSupportedError:
            pass
