class Cloud(object):
    """Cloud

    :ivar name: Name of the cloud

    """
    def add_credential(self, credential):
        """Add or replaces credentials for this cloud.

        :param `juju.Credential` credential: The Credential to add

        """
        raise NotImplementedError()

    def get_credentials(self):
        """Return list of all credentials for this cloud.

        """
        raise NotImplementedError()

    def remove_credential(self, credential_name):
        """Remove a credential for this cloud.

        :param str credential_name: Name of the credential to remove

        """
        raise NotImplementedError()

    def bootstrap(
            self, controller_name, region=None, agent_version=None,
            auto_upgrade=False, bootstrap_constraints=None,
            bootstrap_series=None, config=None, constraints=None,
            credential=None, default_model=None, keep_broken=False,
            metadata_source=None, no_gui=False, to=None,
            upload_tools=False):

        """Initialize a cloud environment.

        :param str controller_name: Name of controller to create
        :param str region: Cloud region in which to bootstrap
        :param str agent_version: Version of tools to use for Juju agents
        :param bool auto_upgrade: Upgrade to latest path release tools on first
            bootstrap
        :param bootstrap_constraints: Constraints for the bootstrap machine
        :type bootstrap_constraints: :class:`juju.Constraints`
        :param str bootstrap_series: Series of the bootstrap machine
        :param dict config: Controller configuration
        :param constraints: Default constraints for all future workload
            machines
        :type constraints: :class:`juju.Constraints`
        :param credential: Credential to use when bootstrapping
        :type credential: :class:`juju.Credential`
        :param str default_model: Name to give the default model
        :param bool keep_broken: Don't destroy model if bootstrap fails
        :param str metadata_source: Local path to use as tools and/or metadata
            source
        :param bool no_gui: Don't install the Juju GUI in the controller when
            bootstrapping
        :param str to: Placement directive for bootstrap node (typically used
            with MAAS)
        :param bool upload_tools: Upload local version of tools before
            bootstrapping

        """
        raise NotImplementedError()

    def set_default_credential(self, credential_name):
        """Set the default credentials for this cloud.

        :param str credential_name: Credential to make default

        """
        raise NotImplementedError()

    def set_default_region(self, region):
        """Set the default region for this cloud.

        :param str region: Name of region to make default

        """
        raise NotImplementedError()
