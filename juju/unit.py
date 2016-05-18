class Unit(object):
    def add_storage(self, name, constraints=None):
        """Add unit storage dynamically.

        :param str name: Storage name, as specified by the charm
        :param str constraints: Comma-separated list of constraints in the
            form 'POOL,COUNT,SIZE'

        """
        pass

    def collect_metrics(self):
        """Collect metrics on this unit.

        """
        pass

    def destroy(self):
        """Destroy this unit.

        """
        pass
    remove = destroy

    def get_resources(self, details=False):
        """Return resources for this unit.

        :param bool details: Include detailed info about resources used by each
            unit

        """
        pass

    def run(self):
        """Run command on this unit.

        """
        pass

    def run_action(self):
        """Run action on this unit.

        """
        pass

    def scp(self):
        """Transfer files to this unit.

        """
        pass

    def set_meter_status(self):
        """Set the meter status on this unit.

        """
        pass

    def ssh(self):
        """Execute a command over SSH on this unit.

        """
        pass

    def status_history(self):
        """Get status history for this unit.

        """
        pass
