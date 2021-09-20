import pytest

from juju.juju import Juju
from .. import base


@base.bootstrapped
@pytest.mark.asyncio
async def test_get_controllers(event_loop):
    async with base.CleanController() as controller:
        j = Juju()

        controllers = j.get_controllers()
        assert isinstance(controllers, dict)
        assert len(controllers) >= 1
        assert controller.controller_name in controllers
