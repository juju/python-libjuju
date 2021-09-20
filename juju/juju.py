from juju.controller import Controller
from juju.client.jujudata import FileJujuData
from juju.errors import JujuError


class Juju(object):

    def __init__(self, jujudata=None):
        self.jujudata = jujudata or FileJujuData()

    def add_cloud(self, name, definition, replace=False):
        """Add a user-defined cloud to Juju from among known cloud types.

        :param str name: Name of cloud
        :param dict definition: Cloud definition

        Example cloud definition, as yaml::

            type: openstack
            auth-types: [ userpass ]
            regions:
              london:
                endpoint: https://london.mycloud.com:35574/v3.0/

        """
        raise NotImplementedError()

    def agree(self, *terms):
        """Agree to the terms of a charm.

        :param str *terms: Terms to agree to

        """
        raise NotImplementedError()

    def autoload_credentials(self):
        """Finds cloud credentials and caches them for use by Juju when
        bootstrapping.

        """
        raise NotImplementedError()

    def get_clouds(self):
        """Return list of all available clouds.

        """
        raise NotImplementedError()

    def get_controllers(self):
        """Return list of all available controllers.

        """
        return self.jujudata.controllers()

    def get_plans(self, charm_url):
        """Return list of plans available for the specified charm.

        :param str charm_url: Charm url

        """
        raise NotImplementedError()

    def register(self, registration_string):
        """Register a user to a controller.

        :param str registration_string: The registration string

        """
        raise NotImplementedError()

    def get_cloud(self, name):
        """Get a cloud by name.

        :param str name: Name of cloud

        """
        raise NotImplementedError()

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

    def update_clouds(self):
        """Update public cloud info available to Juju.

        """
        raise NotImplementedError()

    def version(self):
        """Return the Juju version.

        """
        raise NotImplementedError()
