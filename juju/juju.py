class Juju(object):
    def add_cloud(self):
        """Add a user-defined cloud to Juju from among known cloud types.

        """
        pass

    def agree(self):
        """Agree to the terms of a charm.

        """
        pass

    def autoload_credentials(self):
        """Finds cloud credentials and caches them for use by Juju when
        bootstrapping.

        """
        pass

    def create_budget(self):
        """Create a new budget.

        """
        pass

    def get_agreements(self):
        """Return list of terms to which the current user has agreed.

        """
        pass

    def get_budgets(self):
        """Return list of available budgets.

        """
        pass

    def get_clouds(self):
        """Return list of all available clouds.

        """
        pass

    def get_controllers(self):
        """Return list of all available controllers.

        (maybe move this to Cloud?)
        """
        pass

    def get_plans(self, charm_name):
        """Return list of plans available for the specified charm.

        """
        pass

    def register(self, registration_string):
        """Register a user to a controller.

        """
        pass

    def set_budget(self, name, amount):
        """Set a budget limit.

        """
        pass

    def get_cloud(self, name):
        """Get a cloud by name.

        """
        pass

    def get_controller(self):
        """Get a controller by name.

        (maybe move this to Cloud?)
        """
        pass

    def update_clouds(self):
        """Update public cloud info available to Juju.

        """
        pass

    def version(self):
        """Return the Juju version.

        """
        pass
