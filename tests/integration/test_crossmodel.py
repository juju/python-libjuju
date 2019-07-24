import asyncio
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import mock
import paramiko

import pylxd
import pytest
from juju.client.client import ApplicationFacade, ConfigValue
from juju.errors import JujuError
from juju.model import Model, ModelObserver
from juju.utils import block_until, run_with_interrupt

from .. import base


@base.bootstrapped
@pytest.mark.asyncio
async def test_offer(event_loop):
    async with base.CleanModel() as model:
        application = await model.deploy(
            'cs:~jameinel/ubuntu-lite-7',
            application_name='ubuntu',
            series='bionic',
            channel='stable',
        )
        assert 'ubuntu-lite' in model.applications
        await model.block_until(
            lambda: all(unit.workload_status == 'active'
                        for unit in application.units))
        await model.offer("mysql:db")
