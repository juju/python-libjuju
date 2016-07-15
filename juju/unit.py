import logging

from . import model
from .client import client

log = logging.getLogger(__name__)


class Unit(model.ModelEntity):
    def _get_tag(self):
        return 'unit-{}'.format(self.data['name'].replace('/', '-'))

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

    def resolved(self, retry=False):
        """Mark unit errors resolved.

        :param bool retry: Re-execute failed hooks

        """
        pass

    async def run(self, command, timeout=None):
        """Run command on this unit.

        :param str command: The command to run
        :param int timeout: Time to wait before command is considered failed

        """
        action = client.ActionFacade()
        conn = await self.model.connection.clone()
        action.connect(conn)

        log.debug(
            'Running `%s` on %s', command, self.name)

        return await action.Run(
            [],
            command,
            [],
            timeout,
            [self.name],
        )

    def run_action(self, action_name, **params):
        """Run action on this unit.

        :param str action_name: Name of action to run
        :param \*\*params: Action parameters

        """
        pass

    def scp(
            self, source_path, user=None, destination_path=None, proxy=False,
            scp_opts=None):
        """Transfer files to this unit.

        :param str source_path: Path of file(s) to transfer
        :param str user: Remote username
        :param str destination_path: Destination of transferred files on
            remote machine
        :param bool proxy: Proxy through the Juju API server
        :param str scp_opts: Additional options to the `scp` command

        """
        pass

    def set_meter_status(self):
        """Set the meter status on this unit.

        """
        pass

    def ssh(
            self, command, user=None, proxy=False, ssh_opts=None):
        """Execute a command over SSH on this unit.

        :param str command: Command to execute
        :param str user: Remote username
        :param bool proxy: Proxy through the Juju API server
        :param str ssh_opts: Additional options to the `ssh` command

        """
        pass

    def status_history(self, num=20, utc=False):
        """Get status history for this unit.

        :param int num: Size of history backlog
        :param bool utc: Display time as UTC in RFC3339 format

        """
        pass
