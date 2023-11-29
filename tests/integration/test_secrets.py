# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import pytest
from .. import base


@base.bootstrapped
@pytest.mark.bundle
async def test_add_secret(event_loop):

    async with base.CleanModel() as model:
        secret = await model.add_secret(name='my-apitoken', dataArgs=['token=34ae35facd4'])
        assert secret.startswith('secret:')

        secrets = await model.list_secrets()
        assert len(secrets) == 1
        assert secrets[0].label == 'my-apitoken'
