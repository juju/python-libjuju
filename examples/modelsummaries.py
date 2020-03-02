"""
This example:

1. Connects to the current model
2. Starts an AllWatcher
3. Prints all changes received from the AllWatcher
4. Runs forever (kill with Ctrl-C)

"""
import asyncio
import logging

from juju import loop
from juju.controller import Controller


async def watch():
    controller = Controller()
    # connect to current
    # controller with current user, per Juju CLI
    await controller.connect()

    # Need to call the WatchModelSummaries or WatchAllModelSummaries on the
    # controller.
    def callback(summary):
        print("-- change --\n{}\n".format(summary))

    await controller.watch_model_summaries(callback)

    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)
    logging.getLogger('juju.client.connection').setLevel(logging.INFO)
    # Run loop until the process is manually stopped (watch will loop
    # forever).
    loop.run(watch())
