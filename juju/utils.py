import asyncio
import os
from collections import defaultdict
from functools import partial
from pathlib import Path


async def execute_process(*cmd, log=None, loop=None):
    '''
    Wrapper around asyncio.create_subprocess_exec.

    '''
    p = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            loop=loop)
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


class IdQueue:
    """
    Wrapper around asyncio.Queue that maintains a separate queue for each ID.
    """
    def __init__(self, maxsize=0, *, loop=None):
        self._queues = defaultdict(partial(asyncio.Queue, maxsize, loop=loop))

    async def get(self, id):
        value = await self._queues[id].get()
        del self._queues[id]
        if isinstance(value, Exception):
            raise value
        return value

    async def put(self, id, value):
        await self._queues[id].put(value)

    async def put_all(self, value):
        for queue in self._queues.values():
            await queue.put(value)


async def run_with_interrupt(task, event, loop=None):
    """
    Awaits a task while allowing it to be interrupted by an `asyncio.Event`.

    If the task finishes without the event becoming set, the results of the
    task will be returned.  If the event becomes set, the task will be
    cancelled ``None`` will be returned.

    :param task: Task to run
    :param event: An `asyncio.Event` which, if set, will interrupt `task`
        and cause it to be cancelled.
    :param loop: Optional event loop to use other than the default.
    """
    loop = loop or asyncio.get_event_loop()
    event_task = loop.create_task(event.wait())
    done, pending = await asyncio.wait([task, event_task],
                                       loop=loop,
                                       return_when=asyncio.FIRST_COMPLETED)
    for f in pending:
        f.cancel()
    result = [f.result() for f in done if f is not event_task]
    if result:
        return result[0]
    else:
        return None
