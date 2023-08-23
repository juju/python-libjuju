# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from juju.controller import Controller
from juju.juju import Juju
from .. import base


@base.bootstrapped
async def test_get_controllers(event_loop):
    async with base.CleanController() as controller:
        j = Juju()

        controllers = j.get_controllers()
        assert isinstance(controllers, dict)
        assert len(controllers) >= 1
        assert controller.controller_name in controllers

        cc = await j.get_controller(controller.controller_name)
        assert isinstance(cc, Controller)
        assert controller.connection().endpoint == cc.connection().endpoint
        await cc.disconnect()
