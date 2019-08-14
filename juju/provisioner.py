import os
import re
import shlex
import tempfile
import uuid
from subprocess import CalledProcessError

import paramiko

from .client import client

arches = [
    [re.compile(r"amd64|x86_64"), "amd64"],
    [re.compile(r"i?[3-9]86"), "i386"],
    [re.compile(r"(arm$)|(armv.*)"), "armhf"],
    [re.compile(r"aarch64"), "arm64"],
    [re.compile(r"ppc64|ppc64el|ppc64le"), "ppc64el"],
    [re.compile(r"s390x?"), "s390x"],

]


def normalize_arch(rawArch):
    """Normalize the architecture string."""
    for arch in arches:
        if arch[0].match(rawArch):
            return arch[1]


DETECTION_SCRIPT = """#!/bin/bash
set -e
os_id=$(grep '^ID=' /etc/os-release | tr -d '"' | cut -d= -f2)
if [ "$os_id" = 'centos' ]; then
  os_version=$(grep '^VERSION_ID=' /etc/os-release | tr -d '"' | cut -d= -f2)
  echo "centos$os_version"
else
  lsb_release -cs
fi
uname -m
grep MemTotal /proc/meminfo
cat /proc/cpuinfo
"""

INITIALIZE_UBUNTU_SCRIPT = """set -e
(id ubuntu &> /dev/null) || useradd -m ubuntu -s /bin/bash
umask 0077
temp=$(mktemp)
echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' > $temp
install -m 0440 $temp /etc/sudoers.d/90-juju-ubuntu
rm $temp
su ubuntu -c 'install -D -m 0600 /dev/null ~/.ssh/authorized_keys'
export authorized_keys="{}"
if [ ! -z "$authorized_keys" ]; then
    su ubuntu -c 'echo $authorized_keys >> ~/.ssh/authorized_keys'
fi
"""


class SSHProvisioner:
    """Provision a manually created machine via SSH."""
    user = ""
    host = ""
    private_key_path = ""

    def __init__(self, user, host, private_key_path):
        self.host = host
        self.user = user
        self.private_key_path = private_key_path

    def _get_ssh_client(self, host, user, key):
        """Return a connected Paramiko ssh object.

        :param str host: The host to connect to.
        :param str user: The user to connect as.
        :param str key: The private key to authenticate with.

        :return: object: A paramiko.SSHClient
        :raises: :class:`paramiko.ssh_exception.SSHException` if the
            connection failed
        """

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        pkey = None

        # Read the private key into a paramiko.RSAKey
        if os.path.exists(key):
            with open(key, 'r') as f:
                pkey = paramiko.RSAKey.from_private_key(f)

        #######################################################################
        # There is a bug in some versions of OpenSSH 4.3 (CentOS/RHEL5) where #
        # the server may not send the SSH_MSG_USERAUTH_BANNER message except  #
        # when responding to an auth_none request. For example, paramiko will #
        # attempt to use password authentication when a password is set, but  #
        # the server could deny that, instead requesting keyboard-interactive.#
        # The hack to workaround this is to attempt a reconnect, which will   #
        # receive the right banner, and authentication can proceed. See the   #
        # following for more info:                                            #
        # https://github.com/paramiko/paramiko/issues/432                     #
        # https://github.com/paramiko/paramiko/pull/438                       #
        #######################################################################

        try:
            ssh.connect(host, port=22, username=user, pkey=pkey)
        except paramiko.ssh_exception.SSHException as e:
            if 'Error reading SSH protocol banner' == str(e):
                # Once more, with feeling
                ssh.connect(host, port=22, username=user, pkey=pkey)
            else:
                # Reraise the original exception
                raise e

        return ssh

    def _run_command(self, ssh, cmd, pty=True):
        """Run a command remotely via SSH.

        :param object ssh: The SSHClient
        :param str cmd: The command to execute
        :param list cmd: The `shlex.split` command to execute
        :param bool pty: Whether to allocate a pty

        :return: tuple: The stdout and stderr of the command execution
        :raises: :class:`CalledProcessError` if the command fails
        """

        if isinstance(cmd, str):
            cmd = shlex.split(cmd)

        if type(cmd) is not list:
            cmd = [cmd]

        cmds = ' '.join(cmd)
        stdin, stdout, stderr = ssh.exec_command(cmds, get_pty=pty)
        retcode = stdout.channel.recv_exit_status()

        if retcode > 0:
            output = stderr.read().strip()
            raise CalledProcessError(returncode=retcode, cmd=cmd,
                                     output=output)
        return (
            stdout.read().decode('utf-8').strip(),
            stderr.read().decode('utf-8').strip()
        )

    def _init_ubuntu_user(self):
        """Initialize the ubuntu user.

        :return: bool: If the initialization was successful
        :raises: :class:`paramiko.ssh_exception.AuthenticationException`
            if the authentication fails
        """

        ssh = None
        try:
            # Run w/o allocating a pty, so we fail if sudo prompts for a passwd
            ssh = self._get_ssh_client(
                self.host,
                self.user,
                self.private_key_path,
            )
            stdout, stderr = self._run_command(ssh, "sudo -n true", pty=False)
        except paramiko.ssh_exception.AuthenticationException as e:
            raise e
        finally:
            if ssh:
                ssh.close()

        # Infer the public key
        public_key = None
        public_key_path = "{}.pub".format(self.private_key_path)

        if not os.path.exists(public_key_path):
            raise FileNotFoundError(
                "Public key '{}' doesn't exist.".format(public_key_path)
            )

        with open(public_key_path, "r") as f:
            public_key = f.readline()

        script = INITIALIZE_UBUNTU_SCRIPT.format(public_key)

        try:
            ssh = self._get_ssh_client(
                self.host,
                self.user,
                self.private_key_path,
            )

            self._run_command(
                ssh,
                ["sudo", "/bin/bash -c " + shlex.quote(script)],
                pty=True
            )
        except paramiko.ssh_exception.AuthenticationException as e:
            raise e
        finally:
            ssh.close()

        return True

    def _detect_hardware_and_os(self, ssh):
        """Detect the target hardware capabilities and OS series.

        :param object ssh: The SSHClient
        :return: str: A raw string containing OS and hardware information.
        """

        info = {
            'series': '',
            'arch': '',
            'cpu-cores': '',
            'mem': '',
        }

        stdout, stderr = self._run_command(
            ssh,
            ["sudo", "/bin/bash -c " + shlex.quote(DETECTION_SCRIPT)],
            pty=True,
        )

        lines = stdout.split("\n")
        info['series'] = lines[0].strip()
        info['arch'] = normalize_arch(lines[1].strip())

        memKb = re.split(r'\s+', lines[2])[1]

        # Convert megabytes -> kilobytes
        info['mem'] = round(int(memKb) / 1024)

        # Detect available CPUs
        recorded = {}
        for line in lines[3:]:
            physical_id = ""
            print(line)

            if line.find("physical id") == 0:
                physical_id = line.split(":")[1].strip()
            elif line.find("cpu cores") == 0:
                cores = line.split(":")[1].strip()

                if physical_id not in recorded.keys():
                    info['cpu-cores'] += cores
                    recorded[physical_id] = True

        return info

    def provision_machine(self):
        """Perform the initial provisioning of the target machine.

        :return: bool: The client.AddMachineParams
        :raises: :class:`paramiko.ssh_exception.AuthenticationException`
            if the upload fails
        """
        params = client.AddMachineParams()

        if self._init_ubuntu_user():
            try:

                ssh = self._get_ssh_client(
                    self.host,
                    self.user,
                    self.private_key_path
                )

                hw = self._detect_hardware_and_os(ssh)
                params.series = hw['series']
                params.instance_id = "manual:{}".format(self.host)
                params.nonce = "manual:{}:{}".format(
                    self.host,
                    str(uuid.uuid4()),  # a nop for Juju w/manual machines
                )
                params.hardware_characteristics = {
                    'arch': hw['arch'],
                    'mem': int(hw['mem']),
                    'cpu-cores': int(hw['cpu-cores']),
                }
                params.addresses = [{
                    'value': self.host,
                    'type': 'ipv4',
                    'scope': 'public',
                }]

            except paramiko.ssh_exception.AuthenticationException as e:
                raise e
            finally:
                ssh.close()

        return params

    async def install_agent(self, connection, nonce, machine_id):
        """
        :param object connection: Connection to Juju API
        :param str nonce: The nonce machine specification
        :param str machine_id: The id assigned to the machine

        :return: bool: If the initialization was successful
        """

        # The path where the Juju agent should be installed.
        data_dir = "/var/lib/juju"

        # Disabling this prevents `apt-get update` from running initially, so
        # charms will fail to deploy
        disable_package_commands = False

        client_facade = client.ClientFacade.from_connection(connection)
        results = await client_facade.ProvisioningScript(
            data_dir=data_dir,
            disable_package_commands=disable_package_commands,
            machine_id=machine_id,
            nonce=nonce,
        )

        self._run_configure_script(results.script)

    def _run_configure_script(self, script):
        """Run the script to install the Juju agent on the target machine.

        :param str script: The script returned by the ProvisioningScript API
        :raises: :class:`paramiko.ssh_exception.AuthenticationException`
            if the upload fails
        """

        _, tmpFile = tempfile.mkstemp()
        with open(tmpFile, 'w') as f:
            f.write(script)

        try:
            # get ssh client
            ssh = self._get_ssh_client(
                self.host,
                "ubuntu",
                self.private_key_path,
            )

            # copy the local copy of the script to the remote machine
            sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
            sftp.put(
                tmpFile,
                tmpFile,
            )

            # run the provisioning script
            stdout, stderr = self._run_command(
                ssh,
                "sudo /bin/bash {}".format(tmpFile),
            )

        except paramiko.ssh_exception.AuthenticationException as e:
            raise e
        finally:
            os.remove(tmpFile)
            ssh.close()
