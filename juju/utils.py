import asyncio
import os
from pathlib import Path


async def execute_process(*cmd, log=None):
    '''
    Wrapper around asyncio.create_subprocess_exec.

    '''
    p = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            )
    stdout, stderr = await p.communicate()
    if log:
        log.debug("Exec %s -> %d", cmd, p.returncode)
        if stdout:
            log.debug(stdout.decode('utf-8'))
        if stderr:
            log.debug(stderr.decode('utf-8'))
    return p.returncode == 0


def _read_ssh_key():
    '''
    Inner function for read_ssh_key, suitable for passing to our
    Executor.

    '''
    default_data_dir = Path(Path.home(), ".local", "share", "juju")
    juju_data = os.environ.get("JUJU_DATA", default_data_dir)
    ssh_key_path = Path(juju_data, 'ssh', 'juju_id_rsa.pub')
    with ssh_key_path.open('r') as ssh_key_file:
        ssh_key = ssh_key_file.readlines()[0].strip()
    return ssh_key


async def read_ssh_key(loop):
    '''
    Attempt to read the local juju admin's public ssh key, so that it
    can be passed on to a model.

    '''
    return await loop.run_in_executor(None, _read_ssh_key)
