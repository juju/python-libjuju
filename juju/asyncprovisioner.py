import os
import re
import shlex
import tempfile
import uuid
from subprocess import CalledProcessError

import asyncio
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

    async def _scp(self, source_file, destination_file):
        """Execute an scp command. Requires a fully qualified source and
        destination.

        :param str source_file: Path to the source file
        :param str destination_file: Path to the destination file
        """
        cmd = [
            "scp",
            "-i",
            os.path.expanduser(self.private_key_path),
            "-o",
            "StrictHostKeyChecking=no",
            "-q",
            "-B",
        ]
        destination = "{}@{}:{}".format(self.user, self.host, destination_file)
        cmd.extend([source_file, destination])
        process = await asyncio.create_subprocess_exec(*cmd)
        await process.wait()
        if process.returncode != 0:
            raise CalledProcessError(returncode=process.returncode, cmd=cmd)

    async def _ssh(self, command):
        """Run a command remotely via SSH.

        :param str command: The command to execute
        :return: tuple: The stdout and stderr of the command execution
        :raises: :class:`CalledProcessError` if the command fails
        """

        destination = "{}@{}".format(self.user, self.host)
        cmd = [
            "ssh",
            "-i",
            os.path.expanduser(self.private_key_path),
            "-o",
            "StrictHostKeyChecking=no",
            "-q",
            destination,
        ]
        cmd.extend([command])
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            output = stderr.decode("utf-8").strip()
            raise CalledProcessError(
                returncode=process.returncode, cmd=cmd, output=output
            )
        return (stdout.decode("utf-8").strip(), stderr.decode("utf-8").strip())

    async def _init_ubuntu_user(self):
        """Initialize the ubuntu user.

        :return: bool: If the initialization was successful
        :raises: :class:`CalledProcessError` if the _ssh command fails
        """

        stdout, stderr = await self._ssh("sudo -n true")

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

        stdout, stderr = await self._run_configure_script(script)

        return True

    async def _detect_hardware_and_os(self):
        """Detect the target hardware capabilities and OS series.

        :return: str: A raw string containing OS and hardware information.
        """

        info = {
            "series": "",
            "arch": "",
            "cpu-cores": "",
            "mem": "",
        }

        stdout, stderr = await self._run_configure_script(DETECTION_SCRIPT)

        lines = stdout.split("\n")
        info["series"] = lines[0].strip()
        info["arch"] = normalize_arch(lines[1].strip())

        memKb = re.split(r"\s+", lines[2])[1]

        # Convert megabytes -> kilobytes
        info["mem"] = round(int(memKb) / 1024)

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
                    info["cpu-cores"] += cores
                    recorded[physical_id] = True

        return info

    async def provision_machine(self):
        """Perform the initial provisioning of the target machine.

        :return: bool: The client.AddMachineParams
        """
        params = client.AddMachineParams()

        if await self._init_ubuntu_user():
            hw = await self._detect_hardware_and_os()
            params.series = hw["series"]
            params.instance_id = "manual:{}".format(self.host)
            params.nonce = "manual:{}:{}".format(
                self.host, str(uuid.uuid4()),  # a nop for Juju w/manual machines
            )
            params.hardware_characteristics = {
                "arch": hw["arch"],
                "mem": int(hw["mem"]),
                "cpu-cores": int(hw["cpu-cores"]),
            }
            params.addresses = [
                {"value": self.host, "type": "ipv4", "scope": "public",}
            ]

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

        await self._run_configure_script(results.script)

    async def _run_configure_script(self, script, root=True):
        """Run the script to install the Juju agent on the target machine.

        :param str script: The script to be executed
        """
        _, tmpFile = tempfile.mkstemp()
        with open(tmpFile, "w") as f:
            f.write(script)
            f.close()

        # copy the local copy of the script to the remote machine
        sftp = await self._scp(tmpFile, tmpFile)

        # run the provisioning script
        return await self._ssh(
            "{} /bin/bash {}".format("sudo" if root else "", tmpFile)
        )
