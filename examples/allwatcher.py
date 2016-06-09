import asyncio

from juju.client.connection import Connection
from juju.client import watcher


loop = asyncio.get_event_loop()
conn = loop.run_until_complete(Connection.connect_current())


async def watch():
    allwatcher = watcher.AllWatcher()
    allwatcher.connect(conn)
    while True:
        change = await allwatcher.Next()
        for delta in change.deltas:
            print(delta.deltas)

loop.run_until_complete(watch())
