class Controller(object):
    def add_model(self, name, config=None, credential=None, owner=None):
        """Add a model to this controller.

        :param str name: Name of the model
        :param dict config: Model configuration
        :param str credential: e.g. '<cloud>:<credential>'
        :param str owner: Owner username

        """
        pass

    def add_user(self, username, display_name=None, acl=None, models=None):
        """Add a user to this controller.

        :param str username: Username
        :param str display_name: Display name
        :param str acl: Access control, e.g. 'read'
        :param list models: Models to which the user is granted access

        """
        pass

    def change_user_password(self, username, password):
        """Change the password for a user in this controller.

        :param str username: Username
        :param str password: New password

        """
        pass

    def destroy(self, destroy_all_models=False):
        """Destroy this controller.

        :param bool destroy_all_models: Destroy all hosted models in the
            controller.

        """
        pass

    def disable_user(self, username):
        """Disable a user.

        :param str username: Username

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

    def get_models(self, all_=False, username=None):
        """Return list of available models on this controller.

        :param bool all_: List all models, regardless of user accessibilty
            (admin use only)
        :param str username: User for which to list models (admin use only)

        """
        pass

    def get_payloads(self, *patterns):
        """Return list of known payloads.

        :param str \*patterns: Patterns to match against

        Each pattern will be checked against the following info in Juju::

            - unit name
            - machine id
            - payload type
            - payload class
            - payload id
            - payload tag
            - payload status

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
