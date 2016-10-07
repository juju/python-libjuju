"""
This example:

1. Connects to the current model
2. Starts an AllWatcher
3. Prints all changes received from the AllWatcher
4. Runs forever (kill with Ctrl-C)

"""
import asyncio
import logging

from juju.client.connection import Connection
from juju.client import watcher


async def watch():
    allwatcher = watcher.AllWatcher()
    allwatcher.connect(conn)
    while True:
        change = await allwatcher.Next()
        for delta in change.deltas:
            print(delta.deltas)


logging.basicConfig(level=logging.DEBUG)
loop = asyncio.get_event_loop()
conn = loop.run_until_complete(Connection.connect_current())
loop.run_until_complete(watch())
