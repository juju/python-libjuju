class Service(object):
    def add_relation(self):
        """Add a relation to another service.

        """
        pass

    def add_unit(self):
        """Add one or more units to this service.

        """
        pass
    add_units = add_unit

    def allocate(self):
        """Allocate budget to this service.

        """
        pass

    def attach(self):
        """Upload a file as a resource for this service.

        """
        pass

    def collect_metrics(self):
        """Collect metrics on this service.

        """
        pass

    def destroy_relation(self):
        """Remove a relation to another service.

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

    def get_actions(self):
        """Get actions defined for this service.

        """
        pass

    def get_resources(self):
        """Return resources for this service.

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
