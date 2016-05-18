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

    def run(self):
        """Run command on all units for this service.

        """
        pass

    def set_config(self):
        """Set configuration options for this service.

        """
        pass

    def set_constraints(self):
        """Set machine constraints for this service.

        """
        pass

    def set_meter_status(self):
        """Set the meter status on this status.

        """
        pass

    def set_plan(self):
        """Set the plan for this service, effective immediately.

        """
        pass

    def unexpose(self):
        """Remove public availability over the network for this service.

        """
        pass

    def update_allocation(self):
        """Update existing allocation for this service.

        """
        pass

    def upgrade_charm(self):
        """Upgrade the charm for this service.

        """
        pass
