class Service(object):
    def add_relation(self, local_relation, remote_relation):
        """Add a relation to another service.

        :param str local_relation: Name of relation on this service
        :param str remote_relation: Name of relation on the other service in
            the form '<service>[:<relation_name>]'

        """
        pass

    def add_unit(self, count=1, to=None):
        """Add one or more units to this service.

        :param int count: Number of units to add
        :param str to: Placement directive, e.g.::
            '23' - machine 23
            'lxc:7' - new lxc container on machine 7
            '24/lxc/3' - lxc container 3 or machine 24

            If None, a new machine is provisioned.

        """
        pass
    add_units = add_unit

    def allocate(self, budget, value):
        """Allocate budget to this service.

        :param str budget: Name of budget
        :param int value: Budget limit

        """
        pass

    def attach(self, resource_name, file_path):
        """Upload a file as a resource for this service.

        :param str resource: Name of the resource
        :param str file_path: Path to the file to upload

        """
        pass

    def collect_metrics(self):
        """Collect metrics on this service.

        """
        pass

    def destroy_relation(self, local_relation, remote_relation):
        """Remove a relation to another service.

        :param str local_relation: Name of relation on this service
        :param str remote_relation: Name of relation on the other service in
            the form '<service>[:<relation_name>]'

        """
        pass
    remove_relation = destroy_relation

    def destroy(self):
        """Remove this service from the model.

        """
        pass
    remove = destroy

    def expose(self):
        """Make this service publicly available over the network.

        """
        pass

    def get_config(self):
        """Return the configuration settings for this service.

        """
        pass

    def get_constraints(self):
        """Return the machine constraints for this service.

        """
        pass

    def get_actions(self, schema=False):
        """Get actions defined for this service.

        :param bool schema: Return the full action schema

        """
        pass

    def get_resources(self, details=False):
        """Return resources for this service.

        :param bool details: Include detailed info about resources used by each
            unit

        """
        pass

    def run(self, command, timeout=None):
        """Run command on all units for this service.

        :param str command: The command to run
        :param int timeout: Time to wait before command is considered failed

        """
        pass

    def set_config(self, to_default=False, **config):
        """Set configuration options for this service.

        :param bool to_default: Set service options to default values
        :param \*\*config: Config key/values

        """
        pass

    def set_constraints(self, constraints):
        """Set machine constraints for this service.

        :param :class:`juju.Constraints` constraints: Machine constraints

        """
        pass

    def set_meter_status(self, status, info=None):
        """Set the meter status on this status.

        :param str status: Meter status, e.g. 'RED', 'AMBER'
        :param str info: Extra info message

        """
        pass

    def set_plan(self, plan_name):
        """Set the plan for this service, effective immediately.

        :param str plan_name: Name of plan

        """
        pass

    def unexpose(self):
        """Remove public availability over the network for this service.

        """
        pass

    def update_allocation(self, allocation):
        """Update existing allocation for this service.

        :param int allocation: The allocation to set

        """
        pass

    def upgrade_charm(
            self, channel=None, force_series=False, force_units=False,
            path=None, resources=None, revision=-1, switch=None):
        """Upgrade the charm for this service.

        :param str channel: Channel to use when getting the charm from the
            charm store, e.g. 'development'
        :param bool force_series: Upgrade even if series of deployed service
            is not supported by the new charm
        :param bool force_units: Upgrade all units immediately, even if in
            error state
        :param str path: Uprade to a charm located at path
        :param dict resources: Dictionary of resource name/filepath pairs
        :param int revision: Explicit upgrade revision
        :param str switch: Crossgrade charm url

        """
        pass
