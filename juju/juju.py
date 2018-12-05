class Juju(object):
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

    def create_budget(self):
        """Create a new budget.

        """
        raise NotImplementedError()

    def get_agreements(self):
        """Return list of terms to which the current user has agreed.

        """
        raise NotImplementedError()

    def get_budgets(self):
        """Return list of available budgets.

        """
        raise NotImplementedError()

    def get_clouds(self):
        """Return list of all available clouds.

        """
        raise NotImplementedError()

    def get_controllers(self):
        """Return list of all available controllers.

        (maybe move this to Cloud?)
        """
        raise NotImplementedError()

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

    def set_budget(self, name, limit):
        """Set a monthly budget limit.

        :param str name: Name of budget
        :param int limit: Monthly limit

        """
        raise NotImplementedError()

    def get_cloud(self, name):
        """Get a cloud by name.

        :param str name: Name of cloud

        """
        raise NotImplementedError()

    def get_controller(self, name, include_passwords=False):
        """Get a controller by name.

        :param str name: Name of controller
        :param bool include_passwords: Include passwords for accounts

        (maybe move this to Cloud?)
        """
        raise NotImplementedError()

    def update_clouds(self):
        """Update public cloud info available to Juju.

        """
        raise NotImplementedError()

    def version(self):
        """Return the Juju version.

        """
        raise NotImplementedError()
