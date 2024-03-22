# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import asyncio

import pytest

from .. import base


@base.bootstrapped
@pytest.mark.asyncio
async def test_status(event_loop):
    async with base.CleanModel() as model:
        await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='jammy',
            channel='stable',
        )

        await asyncio.wait_for(
            model.block_until(lambda: len(model.machines)),
            timeout=240)
        machine = model.machines['0']

        assert machine.status in ('allocating', 'pending')
        assert machine.agent_status == 'pending'
        assert not machine.agent_version

        # there is some inconsistency in the capitalization of status_message
        # between different providers
        await asyncio.wait_for(
            model.block_until(
                lambda: (machine.status == 'running' and
                         machine.status_message.lower() == 'running' and
                         machine.agent_status == 'started')),
            timeout=480)
