"""
This example:

1. Connects to the current model
2. Starts an AllWatcher
3. Prints all changes received from the AllWatcher
4. Runs forever (kill with Ctrl-C)

"""
import logging

from juju import loop
from juju.client import client
from juju.model import Model


async def watch():
    model = Model()
    await model.connect()

    allwatcher = client.AllWatcherFacade.from_connection(model.connection())
    while True:
        change = await allwatcher.Next()
        for delta in change.deltas:
            print(delta.deltas)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)
    # Run loop until the process is manually stopped (watch will loop
    # forever).
    loop.run(watch())
