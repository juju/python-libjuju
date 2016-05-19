class Model(object):
    def add_machine(
            self, spec=None, constraints=None, disks=None, series=None,
            count=1):
        """Start a new, empty machine and optionally a container, or add a
        container to a machine.

        :param str spec: Machine specification
            Examples::
                (None) - starts a new machine
                'lxc' - starts a new machine with on lxc container
                'lxc:4' - starts a new lxc container on machine 4
                'ssh:user@10.10.0.3' - manually provisions a machine with ssh
                'zone=us-east-1a' - starts a machine in zone us-east-1s on AWS
                'maas2.name' - acquire machine maas2.name on MAAS
        :param :class:`juju.Constraints` constraints: Machine constraints
        :param list disks: List of disk :class:`constraints <juju.Constraints>`
        :param str series: Series
        :param int count: Number of machines to deploy

        Supported container types are: lxc, lxd, kvm

        When deploying a container to an existing machine, constraints cannot
        be used.

        """
        pass
    add_machines = add_machine

    def add_relation(self, relation1, relation2):
        """Add a relation between two services.

        :param str relation1: '<service>[:<relation_name>]'
        :param str relation2: '<service>[:<relation_name>]'

        """
        pass

    def add_space(self, name, *cidrs):
        """Add a new network space.

        Adds a new space with the given name and associates the given
        (optional) list of existing subnet CIDRs with it.

        :param str name: Name of the space
        :param \*cidrs: Optional list of existing subnet CIDRs

        """
        pass

    def add_ssh_key(self, key):
        """Add a public SSH key to this model.

        :param str key: The public ssh key

        """
        pass
    add_ssh_keys = add_ssh_key

    def add_subnet(self, cidr_or_id, space, *zones):
        """Add an existing subnet to this model.

        :param str cidr_or_id: CIDR or provider ID of the existing subnet
        :param str space: Network space with which to associate
        :param str \*zones: Zone(s) in which the subnet resides

        """
        pass

    def get_backups(self):
        """Retrieve metadata for backups in this model.

        """
        pass

    def block(self, *commands):
        """Add a new block to this model.

        :param str \*commands: The commands to block. Valid values are
            'all-changes', 'destroy-model', 'remove-object'

        """
        pass

    def get_blocks(self):
        """List blocks for this model.

        """
        pass

    def get_cached_images(self, arch=None, kind=None, series=None):
        """Return a list of cached OS images.

        :param str arch: Filter by image architecture
        :param str kind: Filter by image kind, e.g. 'lxd'
        :param str series: Filter by image series, e.g. 'xenial'

        """
        pass

    def create_backup(self, note=None, no_download=False):
        """Create a backup of this model.

        :param str note: A note to store with the backup
        :param bool no_download: Do not download the backup archive
        :return str: Path to downloaded archive

        """
        pass

    def create_storage_pool(self, name, provider_type, **pool_config):
        """Create or define a storage pool.

        :param str name: Name to give the storage pool
        :param str provider_type: Pool provider type
        :param \*\*pool_config: key/value pool configuration pairs

        """
        pass

    def debug_log(
            self, no_tail=False, exclude_module=None, include_module=None,
            include=None, level=None, limit=0, lines=10, replay=False,
            exclude=None):
        """Get log messages for this model.

        :param bool no_tail: Stop after returning existing log messages
        :param list exclude_module: Do not show log messages for these logging
            modules
        :param list include_module: Only show log messages for these logging
            modules
        :param list include: Only show log messages for these entities
        :param str level: Log level to show, valid options are 'TRACE',
            'DEBUG', 'INFO', 'WARNING', 'ERROR,
        :param int limit: Return this many of the most recent (possibly
            filtered) lines are shown
        :param int lines: Yield this many of the most recent lines, and keep
            yielding
        :param bool replay: Yield the entire log, and keep yielding
        :param list exclude: Do not show log messages for these entities

        """
        pass

    def deploy(
            self, entity_url, service_name=None, bind=None, budget=None,
            channel=None, config=None, constraints=None, force=False,
            num_units=1, plan=None, resource=None, series=None, storage=None,
            to=None):
        """Deploy a new service or bundle.

        :param str entity_url: Charm or bundle url
        :param str service_name: Name to give the service
        :param dict bind: <charm endpoint>:<network space> pairs
        :param dict budget: <budget name>:<limit> pairs
        :param str channel: Charm store channel from which to retrieve
            the charm or bundle, e.g. 'development'
        :param dict config: Charm configuration dictionary
        :param :class:`juju.Constraints` constraints: Service constraints
        :param bool force: Allow charm to be deployed to a machine running
            an unsupported series
        :param int num_units: Number of units to deploy
        :param str plan: Plan under which to deploy charm
        :param dict resource: <resource name>:<file path> pairs
        :param str series: Series on which to deploy
        :param dict storage: Storage constraints TODO how do these look?
        :param str to: Placement directive, e.g.::
            '23' - machine 23
            'lxc:7' - new lxc container on machine 7
            '24/lxc/3' - lxc container 3 or machine 24

            If None, a new machine is provisioned.

        """
        pass

    def destroy(self):
        """Terminate all machines and resources for this model.

        """
        pass

    def get_backup(self, archive_id):
        """Download a backup archive file.

        :param str archive_id: The id of the archive to download
        :return str: Path to the archive file

        """
        pass

    def enable_ha(
            self, num_controllers=0, constraints=None, series=None, to=None):
        """Ensure sufficient controllers exist to provide redundancy.

        :param int num_controllers: Number of controllers to make available
        :param :class:`juju.Constraints` constraints: Constraints to apply
            to the controller machines
        :param str series: Series of the controller machines
        :param list to: Placement directives for controller machines, e.g.::
            '23' - machine 23
            'lxc:7' - new lxc container on machine 7
            '24/lxc/3' - lxc container 3 or machine 24

            If None, a new machine is provisioned.

        """
        pass

    def get_config(self):
        """Return the configuration settings for this model.

        """
        pass

    def get_constraints(self):
        """Return the machine constraints for this model.

        """
        pass

    def grant(self, username, acl='read'):
        """Grant a user access to this model.

        :param str username: Username
        :param str acl: Access control ('read' or 'write')

        """
        pass

    def import_ssh_key(self, identity):
        """Add a public SSH key from a trusted indentity source to this model.

        :param str identity: User identity in the form <lp|gh>:<username>

        """
        pass
    import_ssh_keys = import_ssh_key

    def get_machines(self, utc=False):
        """Return list of machines in this model.

        :param bool utc: Display time as UTC in RFC3339 format

        """
        pass

    def get_shares(self):
        """Return list of all users with access to this model.

        """
        pass

    def get_spaces(self):
        """Return list of all known spaces, including associated subnets.

        """
        pass

    def get_ssh_key(self):
        """Return known SSH keys for this model.

        """
        pass
    get_ssh_keys = get_ssh_key

    def get_storage(self, filesystem=False, volume=False):
        """Return details of storage instances.

        :param bool filesystem: Include filesystem storage
        :param bool volume: Include volume storage

        """
        pass

    def get_storage_pools(self, names=None, providers=None):
        """Return list of storage pools.

        :param list names: Only include pools with these names
        :param list providers: Only include pools for these providers

        """
        pass

    def get_subnets(self, space=None, zone=None):
        """Return list of known subnets.

        :param str space: Only include subnets in this space
        :param str zone: Only include subnets in this zone

        """
        pass

    def remove_blocks(self):
        """Remove all blocks from this model.

        """
        pass

    def remove_backup(self, backup_id):
        """Delete a backup.

        :param str backup_id: The id of the backup to remove

        """
        pass

    def remove_cached_images(self, arch=None, kind=None, series=None):
        """Remove cached OS images.

        :param str arch: Architecture of the images to remove
        :param str kind: Image kind to remove, e.g. 'lxd'
        :param str series: Image series to remove, e.g. 'xenial'

        """
        pass

    def remove_machine(self, *machine_ids):
        """Remove a machine from this model.

        :param str \*machine_ids: Ids of the machines to remove

        """
        pass
    remove_machines = remove_machine

    def remove_ssh_key(self, *keys):
        """Remove a public SSH key(s) from this model.

        :param str \*keys: Keys to remove

        """
        pass
    remove_ssh_keys = remove_ssh_key

    def restore_backup(self):
        """Restore a backup archive to a new controller.

        """
        pass

    def retry_provisioning(self):
        """Retry provisioning for failed machines.

        """
        pass

    def revoke(self):
        """Revoke a user's access to this model.

        """
        pass

    def run(self):
        """Run command on all machines in this model.

        """
        pass

    def set_config(self):
        """Set configuration keys on this model.

        """
        pass

    def set_constraints(self):
        """Set machine constraints on this model.

        """
        pass

    def get_action_output(self, action_uuid):
        """Get the results of an action by ID.

        """
        pass

    def get_action_status(self, uuid_or_prefix):
        """Get the status of all actions, filtered by ID or prefix.

        """
        pass

    def get_budget(self, budget_name):
        """Get budget by name.

        """
        pass

    def get_status(self):
        """Return the status of the model.

        """
        pass
    status = get_status

    def sync_tools(self):
        """Copy Juju tools into this model.

        """
        pass

    def unblock(self, operation):
        """Unblock an operation that would alter this model.

        """
        pass

    def unset_config(self):
        """Unset configuration on this model.

        """
        pass

    def upgrade_gui(self):
        """Upgrade the Juju GUI for this model.

        """
        pass

    def upload_backup(self):
        """Store a backup archive remotely in Juju.

        """
        pass
