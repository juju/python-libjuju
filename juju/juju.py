# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from juju.controller import Controller
from juju.client.jujudata import FileJujuData
from juju.errors import JujuError


class Juju(object):

    def __init__(self, jujudata=None):
        self.jujudata = jujudata or FileJujuData()

    def get_controllers(self):
        """Return list of all available controllers.

        """
        return self.jujudata.controllers()

    async def get_controller(self, name, include_passwords=False):
        """Get a controller by name.

        :param str name: Name of controller
        :param bool include_passwords: Include passwords for accounts

        The returned controller will try and connect to be ready to use.
        """

        # check if name is in the controllers.yaml
        controllers = self.jujudata.controllers()
        assert isinstance(controllers, dict)
        if name not in controllers:
            raise JujuError('%s is not among the controllers: %s' % (name, controllers.keys()))

        # make a new Controller object that's connected to the
        # controller with the given name
        controller = Controller()
        await controller.connect(name)
        return controller
