import asyncio
import ipaddress
import logging
import os

import pyrfc3339

from . import model, tag
from .annotationhelper import _get_annotations, _set_annotations
from .client import client
from .errors import JujuError

log = logging.getLogger(__name__)


class Machine(model.ModelEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def destroy(self, force=False):
        """Remove this machine from the model.

        Blocks until the machine is actually removed.

        """
        facade = client.ClientFacade.from_connection(self.connection)

        log.debug(
            'Destroying machine %s', self.id)

        await facade.DestroyMachines(force=force, machine_names=[self.id])
        return await self.model._wait(
            'machine', self.id, 'remove')
    remove = destroy

    def run(self, command, timeout=None):
        """Run command on this machine.

        :param str command: The command to run
        :param int timeout: Time to wait before command is considered failed

        """
        raise NotImplementedError()

    async def get_annotations(self):
        """Get annotations on this machine.

        :return dict: The annotations for this application
        """
        return await _get_annotations(self.tag, self.connection)

    async def set_annotations(self, annotations):
        """Set annotations on this machine.

        :param annotations map[string]string: the annotations as key/value
            pairs.

        """
        return await _set_annotations(self.tag, annotations, self.connection)

    def _format_addr(self, addr):
        """Validate and format IP address.

        :param addr: IPv6 or IPv4 address
        :type addr: str
        :returns: Address string, optionally encapsulated in brackets ([])
        :rtype: str
        :raises: ValueError
        """
        ipaddr = ipaddress.ip_address(addr)
        if isinstance(ipaddr, ipaddress.IPv6Address):
            fmt = '[{}]'
        else:
            fmt = '{}'
        return fmt.format(ipaddr)

    async def scp_to(self, source, destination, user='ubuntu', proxy=False,
                     scp_opts=''):
        """Transfer files to this machine.

        :param str source: Local path of file(s) to transfer
        :param str destination: Remote destination of transferred files
        :param str user: Remote username
        :param bool proxy: Proxy through the Juju API server
        :param scp_opts: Additional options to the `scp` command
        :type scp_opts: str or list
        """
        if proxy:
            raise NotImplementedError('proxy option is not implemented')

        try:
            # if dns_name is an IP address format it appropriately
            address = self._format_addr(self.dns_name)
        except ValueError:
            # otherwise we assume it to be a DNS resolvable string
            address = self.dns_name
        destination = '{}@{}:{}'.format(user, address, destination)
        await self._scp(source, destination, scp_opts)

    async def scp_from(self, source, destination, user='ubuntu', proxy=False,
                       scp_opts=''):
        """Transfer files from this machine.

        :param str source: Remote path of file(s) to transfer
        :param str destination: Local destination of transferred files
        :param str user: Remote username
        :param bool proxy: Proxy through the Juju API server
        :param scp_opts: Additional options to the `scp` command
        :type scp_opts: str or list
        """
        if proxy:
            raise NotImplementedError('proxy option is not implemented')

        try:
            # if dns_name is an IP address format it appropriately
            address = self._format_addr(self.dns_name)
        except ValueError:
            # otherwise we assume it to be a DNS resolvable string
            address = self.dns_name
        source = '{}@{}:{}'.format(user, address, source)
        await self._scp(source, destination, scp_opts)

    async def _scp(self, source, destination, scp_opts):
        """ Execute an scp command. Requires a fully qualified source and
        destination.
        """
        cmd = [
            'scp',
            '-i', os.path.expanduser('~/.local/share/juju/ssh/juju_id_rsa'),
            '-o', 'StrictHostKeyChecking=no',
            '-q',
            '-B'
        ]
        cmd.extend(scp_opts.split() if isinstance(scp_opts, str) else scp_opts)
        cmd.extend([source, destination])
        loop = self.model.loop
        process = await asyncio.create_subprocess_exec(*cmd, loop=loop)
        await process.wait()
        if process.returncode != 0:
            raise JujuError("command failed: %s" % cmd)

    async def ssh(
            self, command, user=None, proxy=False, ssh_opts=None):
        """Execute a command over SSH on this machine.

        :param str command: Command to execute
        :param str user: Remote username
        :param bool proxy: Proxy through the Juju API server
        :param str ssh_opts: Additional options to the `ssh` command

        """
        if proxy:
            raise NotImplementedError('proxy option is not implemented')
        address = self.dns_name
        destination = "{}@{}".format(user, address)
        cmd = [
            'ssh',
            '-i', os.path.expanduser('~/.local/share/juju/ssh/juju_id_rsa'),
            '-o', 'StrictHostKeyChecking=no',
            '-q',
            destination
        ]
        if ssh_opts:
            cmd.extend(ssh_opts.split() if isinstance(ssh_opts, str) else ssh_opts)
        cmd.extend([command])
        loop = self.model.loop
        process = await asyncio.create_subprocess_exec(*cmd, loop=loop)
        await process.wait()
        if process.returncode != 0:
            raise JujuError("command failed: %s" % cmd)

    def status_history(self, num=20, utc=False):
        """Get status history for this machine.

        :param int num: Size of history backlog
        :param bool utc: Display time as UTC in RFC3339 format

        """
        raise NotImplementedError()

    @property
    def agent_status(self):
        """Returns the current Juju agent status string.

        """
        return self.safe_data['agent-status']['current']

    @property
    def agent_status_since(self):
        """Get the time when the `agent_status` was last updated.

        """
        return pyrfc3339.parse(self.safe_data['agent-status']['since'])

    @property
    def agent_version(self):
        """Get the version of the Juju machine agent.

        May return None if the agent is not yet available.
        """
        version = self.safe_data['agent-status']['version']
        if version:
            return client.Number.from_json(version)
        else:
            return None

    @property
    def status(self):
        """Returns the current machine provisioning status string.

        """
        return self.safe_data['instance-status']['current']

    @property
    def status_message(self):
        """Returns the current machine provisioning status message.

        """
        return self.safe_data['instance-status']['message']

    @property
    def status_since(self):
        """Get the time when the `status` was last updated.

        """
        return pyrfc3339.parse(self.safe_data['instance-status']['since'])

    @property
    def dns_name(self):
        """Get the DNS name for this machine. This is a best guess based on the
        addresses available in current data.

        May return None if no suitable address is found.
        """
        for scope in ['public', 'local-cloud']:
            addresses = self.safe_data['addresses'] or []
            addresses = [address for address in addresses
                         if address['scope'] == scope]
            if addresses:
                return addresses[0]['value']
        return None

    @property
    def hostname(self):
        """Get the hostname for this machine as reported by the machine agent
        running on it. This is only supported on 2.8.10+ controllers.

        May return None if no hostname information is available.
        """
        if 'hostname' in self.safe_data and self.safe_data['hostname'] != '':
            return self.safe_data['hostname']
        return None

    @property
    def series(self):
        """Returns the series of the current machine

        """
        return self.safe_data['series']

    @property
    def tag(self):
        return tag.machine(self.id)
