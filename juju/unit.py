class Unit(object):
    def add_storage(self):
        """Add unit storage dynamically.

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

    def get_resources(self):
        """Return resources for this unit.

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
