# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import ipaddress
import logging
import typing

import pyrfc3339

from juju.utils import block_until, juju_ssh_key_paths

from . import jasyncio, model, tag
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
        if self.connection.is_using_old_client:
            # Then we'll use the DestroyMachines from client.ClientFacade
            facade = client.ClientFacade.from_connection(self.connection)
            await facade.DestroyMachines(force=force, machine_names=[self.id])
        else:
            facade = client.MachineManagerFacade.from_connection(self.connection)
            await facade.DestroyMachineWithParams(
                force=force, machine_tags=[tag.machine(self.id)]
            )

        log.debug("Destroying machine %s", self.id)
        return await self.model._wait("machine", self.id, "remove")

    remove = destroy

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
            fmt = "[{}]"
        else:
            fmt = "{}"
        return fmt.format(ipaddr)

    async def scp_to(
        self,
        source,
        destination,
        user="ubuntu",
        proxy=False,
        scp_opts="",
        wait_for_active=False,
        timeout=None,
    ):
        """Transfer files to this machine.

        :param str source: Local path of file(s) to transfer
        :param str destination: Remote destination of transferred files
        :param str user: Remote username
        :param bool proxy: Proxy through the Juju API server
        :param scp_opts: Additional options to the `scp` command
        :type scp_opts: str or list
        :param bool wait_for_active: Wait until the machine is ready to take in ssh commands.
        :param int timeout: Time in seconds to wait until the machine becomes ready.
        """
        if proxy:
            raise NotImplementedError("proxy option is not implemented")
        if wait_for_active:
            await block_until(lambda: self.addresses, timeout=timeout)
        try:
            # if dns_name is an IP address format it appropriately
            address = self._format_addr(self.dns_name)
        except ValueError:
            # otherwise we assume it to be a DNS resolvable string
            address = self.dns_name
        destination = f"{user}@{address}:{destination}"
        await self._scp(source, destination, scp_opts)

    async def scp_from(
        self,
        source,
        destination,
        user="ubuntu",
        proxy=False,
        scp_opts="",
        wait_for_active=False,
        timeout=None,
    ):
        """Transfer files from this machine.

        :param str source: Remote path of file(s) to transfer
        :param str destination: Local destination of transferred files
        :param str user: Remote username
        :param bool proxy: Proxy through the Juju API server
        :param scp_opts: Additional options to the `scp` command
        :type scp_opts: str or list
        :param bool wait_for_active: Wait until the machine is ready to take in ssh commands.
        :param int timeout: Time in seconds to wait until the machine becomes ready.
        """
        if proxy:
            raise NotImplementedError("proxy option is not implemented")
        if wait_for_active:
            await block_until(lambda: self.addresses, timeout=timeout)
        try:
            # if dns_name is an IP address format it appropriately
            address = self._format_addr(self.dns_name)
        except ValueError:
            # otherwise we assume it to be a DNS resolvable string
            address = self.dns_name
        source = f"{user}@{address}:{source}"
        await self._scp(source, destination, scp_opts)

    async def _scp(self, source, destination, scp_opts):
        """Execute an scp command. Requires a fully qualified source and
        destination.
        """
        _, id_path = juju_ssh_key_paths()
        cmd = ["scp", "-i", id_path, "-o", "StrictHostKeyChecking=no", "-q", "-B"]
        cmd.extend(scp_opts.split() if isinstance(scp_opts, str) else scp_opts)
        cmd.extend([source, destination])
        # There's a bit of a gap between the time that the machine is assigned an IP and the ssh
        # service is up and listening, which creates a race for the ssh command. So we retry a
        # couple of times until either we run out of attempts, or the ssh command succeeds to
        # mitigate that effect.
        # TODO (cderici): refactor the ssh and scp subcommand processing into a single method.
        retry_backoff = 2
        retries = 10
        for _ in range(retries):
            process = await jasyncio.create_subprocess_exec(*cmd)
            await process.wait()
            if process.returncode == 0:
                break
            await jasyncio.sleep(retry_backoff)
        if process.returncode != 0:
            raise JujuError(f"command failed after {retries} attempts: {cmd}")

    async def ssh(
        self,
        command,
        user="ubuntu",
        proxy=False,
        ssh_opts=None,
        wait_for_active=False,
        timeout=None,
    ):
        """Execute a command over SSH on this machine.

        :param str command: Command to execute
        :param str user: Remote username
        :param bool proxy: Proxy through the Juju API server
        :param str ssh_opts: Additional options to the `ssh` command
        :param bool wait_for_active: Wait until the machine is ready to take in ssh commands.
        :param int timeout: Time in seconds to wait until the machine becomes ready.
        """
        if proxy:
            raise NotImplementedError("proxy option is not implemented")
        if wait_for_active:
            await block_until(lambda: self.addresses, timeout=timeout)
        address = self.dns_name
        destination = f"{user}@{address}"
        _, id_path = juju_ssh_key_paths()
        cmd = [
            "ssh",
            "-i",
            id_path,
            "-o",
            "StrictHostKeyChecking=no",
            "-q",
            destination,
        ]
        if ssh_opts:
            cmd.extend(ssh_opts.split() if isinstance(ssh_opts, str) else ssh_opts)
        cmd.extend([command])

        # There's a bit of a gap between the time that the machine is assigned an IP and the ssh
        # service is up and listening, which creates a race for the ssh command. So we retry a
        # couple of times until either we run out of attempts, or the ssh command succeeds to
        # mitigate that effect.
        retry_backoff = 2
        retries = 10
        for _ in range(retries):
            process = await jasyncio.create_subprocess_exec(
                *cmd, stdout=jasyncio.subprocess.PIPE, stderr=jasyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                break
            await jasyncio.sleep(retry_backoff)
        if process.returncode != 0:
            raise JujuError(
                f"command failed: {cmd} after {retries} attempts, with {stderr.decode()}"
            )
        # stdout is a bytes-like object, returning a string might be more useful
        return stdout.decode()

    @property
    def addresses(self) -> typing.List[str]:
        """Returns the machine addresses."""
        return self.safe_data["addresses"] or []

    @property
    def agent_status(self):
        """Returns the current Juju agent status string."""
        return self.safe_data["agent-status"]["current"]

    @property
    def agent_status_since(self):
        """Get the time when the `agent_status` was last updated."""
        return pyrfc3339.parse(self.safe_data["agent-status"]["since"])

    @property
    def agent_version(self):
        """Get the version of the Juju machine agent.

        May return None if the agent is not yet available.
        """
        version = self.safe_data["agent-status"]["version"]
        if version:
            return client.Number.from_json(version)
        else:
            return None

    @property
    def status(self):
        """Returns the current machine provisioning status string."""
        return self.safe_data["instance-status"]["current"]

    @property
    def status_message(self):
        """Returns the current machine provisioning status message."""
        return self.safe_data["instance-status"]["message"]

    @property
    def status_since(self):
        """Get the time when the `status` was last updated."""
        return pyrfc3339.parse(self.safe_data["instance-status"]["since"])

    @property
    def dns_name(self):
        """Get the DNS name for this machine. This is a best guess based on the
        addresses available in current data.

        May return None if no suitable address is found.
        """
        ordered_scopes = ["public", "local-cloud", "local-fan"]
        ordered_addresses = [
            address
            for scope in ordered_scopes
            for address in self.addresses
            if scope == address["scope"]
        ]

        for address in ordered_addresses:
            scope = address["scope"]
            for check_scope in ordered_scopes:
                if scope == check_scope:
                    return address["value"]
        return None

    @property
    def hostname(self):
        """Get the hostname for this machine as reported by the machine agent
        running on it. This is only supported on 2.8.10+ controllers.

        May return None if no hostname information is available.
        """
        if "hostname" in self.safe_data and self.safe_data["hostname"] != "":
            return self.safe_data["hostname"]
        return None

    @property
    def series(self):
        """Returns the series of the current machine"""
        return self.safe_data["series"]

    @property
    def tag(self):
        return tag.machine(self.id)
