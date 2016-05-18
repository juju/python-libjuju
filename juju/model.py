class Model(object):
    def add_machine(self):
        """Start a new, empty machine and optionally a container, or add a
        container to a machine.

        """
        pass
    add_machines = add_machine

    def add_relation(self):
        """Add a relation between two services.

        """
        pass

    def add_space(self):
        """Add a new network space.

        """
        pass

    def add_ssh_key(self):
        """Add a public SSH key to this model.

        """
        pass
    add_ssh_keys = add_ssh_key

    def add_subnet(self):
        """Add an existing subnet to this model.

        """
        pass

    def get_backups(self):
        """Retrieve metadata for backups in this model.

        """
        pass

    def block(self):
        """Add a new block to this model.

        """
        pass

    def get_blocks(self):
        """List blocks for this model.

        """
        pass

    def get_cached_images(self):
        """Return a list of cached OS images.

        """
        pass

    def create_backup(self):
        """Create a backup of this model.

        """
        pass

    def create_storage_pool(self):
        """Create or define a storage pool.

        """
        pass

    def debug_log(self):
        """Get log messages for this model.

        """
        pass

    def deploy(self):
        """Deploy a new service or bundle.

        """
        pass

    def destroy(self):
        """Terminate all machines and resources for this model.

        """
        pass

    def get_backup(self):
        """Download a backup archive file.

        """
        pass

    def enable_ha(self):
        """Ensure sufficient controllers exist to provide redundancy.

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

    def grant(self):
        """Grant a user access to this model.

        """
        pass

    def import_ssh_key(self):
        """Add a public SSH key from a trusted indentity source to this model.

        """
        pass
    import_ssh_keys = import_ssh_key

    def get_machine(self, machine_id):
        """Get a machine by id.

        """
        pass

    def get_machines(self):
        """Return list of machines in this model.

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

    def get_storage(self):
        """Return details of storage instances.

        """
        pass

    def get_storage_pools(self):
        """Return list of storage pools.

        """
        pass

    def get_subnets(self):
        """Return list of known subnets.

        """
        pass

    def remove_blocks(self):
        """Remove all blocks from this model.

        """
        pass

    def remove_backup(self):
        """Delete a backup.

        """
        pass

    def remove_cached_images(self):
        """Remove cached OS images.

        """
        pass

    def remove_machine(self):
        """Remove a machine from this model.

        """
        pass
    remove_machines = remove_machine

    def remove_ssh_key(self):
        """Remove a public SSH key(s) from this model.

        """
        pass
    remove_ssh_keys = remove_ssh_key

    def resolved(self):
        """Mark unit errors resolved.

        """
        pass

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
