class Controller(object):
    def add_model(self):
        """Add a model to this controller.

        """
        pass

    def add_user(self):
        """Add a user to this controller.

        """
        pass

    def change_user_password(self):
        """Change the password for a user in this controller.

        """
        pass

    def destroy(self):
        """Destroy this controller.

        """
        pass

    def disable_user(self):
        """Disable a user.

        """
        pass

    def enable_user(self):
        """Re-enable a previously disabled user.

        """
        pass

    def kill(self):
        """Forcibly terminate all machines and other associated resources for
        this controller.

        """
        pass

    def get_models(self):
        """Return list of available models on this controller.

        """
        pass

    def get_payloads(self):
        """Return list of known payloads.

        """
        pass

    def get_users(self):
        """Return list of users that can connect to this controller.

        """
        pass

    def login(self):
        """Log in to this controller.

        """
        pass

    def logout(self):
        """Log out of this controller.

        """
        pass

    def get_model(self, name):
        """Get a model by name.

        """
        pass

    def get_user(self, name):
        """Get a user by name.

        """
        pass
