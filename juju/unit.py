import logging

from dateutil.parser import parse as parse_date

from . import model
from .client import client

log = logging.getLogger(__name__)


class Unit(model.ModelEntity):
    @property
    def agent_status(self):
        """Returns the current agent status string.

        """
        return self.safe_data['agent-status']['current']

    @property
    def agent_status_since(self):
        """Get the time when the `agent_status` was last updated.

        """
        return parse_date(self.safe_data['agent-status']['since'])

    @property
    def agent_status_message(self):
        """Get the agent status message.

        """
        return self.safe_data['agent-status']['message']

    @property
    def workload_status(self):
        """Returns the current workload status string.

        """
        return self.safe_data['workload-status']['current']

    @property
    def workload_status_since(self):
        """Get the time when the `workload_status` was last updated.

        """
        return parse_date(self.safe_data['workload-status']['since'])

    @property
    def workload_status_message(self):
        """Get the workload status message.

        """
        return self.safe_data['workload-status']['message']

    @property
    def tag(self):
        return 'unit-%s' % self.name.replace('/', '-')

    def add_storage(self, name, constraints=None):
        """Add unit storage dynamically.

        :param str name: Storage name, as specified by the charm
        :param str constraints: Comma-separated list of constraints in the
            form 'POOL,COUNT,SIZE'

        """
        raise NotImplementedError()

    def collect_metrics(self):
        """Collect metrics on this unit.

        """
        raise NotImplementedError()

    async def destroy(self):
        """Destroy this unit.

        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Destroying %s', self.name)

        return await app_facade.DestroyUnits([self.name])
    remove = destroy

    def get_resources(self, details=False):
        """Return resources for this unit.

        :param bool details: Include detailed info about resources used by each
            unit

        """
        raise NotImplementedError()

    def resolved(self, retry=False):
        """Mark unit errors resolved.

        :param bool retry: Re-execute failed hooks

        """
        raise NotImplementedError()

    async def run(self, command, timeout=None):
        """Run command on this unit.

        :param str command: The command to run
        :param int timeout: Time to wait before command is considered failed
        :returns: A :class:`juju.action.Action` instance.

        """
        action = client.ActionFacade.from_connection(self.connection)

        log.debug(
            'Running `%s` on %s', command, self.name)

        res = await action.Run(
            [],
            command,
            [],
            timeout,
            [self.name],
        )
        return await self.model.wait_for_action(res.results[0].action.tag)

    async def run_action(self, action_name, **params):
        """Run an action on this unit.

        :param str action_name: Name of action to run
        :param \*\*params: Action parameters
        :returns: A :class:`juju.action.Action` instance.

        Note that this only enqueues the action.  You will need to call
        ``action.wait()`` on the resulting `Action` instance if you wish
        to block until the action is complete.

        """
        action_facade = client.ActionFacade.from_connection(self.connection)

        log.debug('Starting action `%s` on %s', action_name, self.name)

        res = await action_facade.Enqueue([client.Action(
            name=action_name,
            parameters=params,
            receiver=self.tag,
        )])
        action = res.results[0].action
        error = res.results[0].error
        if error and error.code == 'not found':
            raise ValueError('Action `%s` not found on %s' % (action_name,
                                                              self.name))
        elif error:
            raise Exception('Unknown action error: %s' % error.serialize())
        action_id = action.tag[len('action-'):]
        log.debug('Action started as %s', action_id)
        # we mustn't use wait_for_action because that blocks until the
        # action is complete, rather than just being in the model
        return await self.model._wait_for_new('action', action_id)

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
        raise NotImplementedError()

    def set_meter_status(self):
        """Set the meter status on this unit.

        """
        raise NotImplementedError()

    def ssh(
            self, command, user=None, proxy=False, ssh_opts=None):
        """Execute a command over SSH on this unit.

        :param str command: Command to execute
        :param str user: Remote username
        :param bool proxy: Proxy through the Juju API server
        :param str ssh_opts: Additional options to the `ssh` command

        """
        raise NotImplementedError()

    def status_history(self, num=20, utc=False):
        """Get status history for this unit.

        :param int num: Size of history backlog
        :param bool utc: Display time as UTC in RFC3339 format

        """
        raise NotImplementedError()

    async def is_leader_from_status(self):
        """
        Check to see if this unit is the leader. Returns True if so, and
        False if it is not, or if leadership does not make sense
        (e.g., there is no leader in this application.)

        This method is a kluge that calls FullStatus in the
        ClientFacade to get its information. Once
        https://bugs.launchpad.net/juju/+bug/1643691 is resolved, we
        should add a simple .is_leader property, and deprecate this
        method.

        """
        app = self.name.split("/")[0]

        c = client.ClientFacade.from_connection(self.connection)

        status = await c.FullStatus(None)

        # FullStatus may be more up to date than our model, and the
        # unit may have gone away, or we may be doing something silly,
        # like trying to fetch leadership for a subordinate, which
        # will not be filed where we expect in the model. In those
        # cases, we may simply return False, as a nonexistent or
        # subordinate unit is not a leader.
        if not status.applications.get(app):
            return False

        if not status.applications[app].get('units'):
            return False

        if not status.applications[app]['units'].get(self.name):
            return False

        return status.applications[app]['units'][self.name].get('leader',
                                                                False)

    async def get_metrics(self):
        """Get metrics for the unit.

        :return: Dictionary of metrics for this unit.

        """
        metrics = await self.model.get_metrics(self.tag)
        return metrics[self.name]
