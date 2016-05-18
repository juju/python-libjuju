class Cloud(object):
    def add_credential(self):
        """Add or replaces credentials for this cloud.

        """
        pass

    def get_credentials(self):
        """Return list of all credentials for this cloud.

        """
        pass

    def remove_credential(self):
        """Remove a credential for this cloud.

        """
        pass

    def bootstrap(self):
        """Initialize a cloud environment.

        """
        pass

    def set_default_credential(self):
        """Set the default credentials for this cloud.

        """
        pass

    def set_default_region(self):
        """Set the default region for this cloud.

        """
        pass
