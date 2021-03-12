#!/usr/bin/env python3.5

"""
This example:

1. Connects to the current model
2. Creates a machine
3. Waits for the machine agent to start and prints out the reported machine
   hostname.

NOTE: this example requires a 2.8.10+ controller.
"""
import logging

from juju import loop
from juju.model import Model

MB = 1
GB = 1024


async def main():
    model = Model()
    await model.connect()

    try:
        # Add a machine and wait until the machine agents starts
        machine1 = await model.add_machine()
        await model.block_until(
            lambda: machine1.agent_status == 'started')

        # At this point we can access the reported hostname via the hostname
        # property of the machine model.
        print("machine1 hostname: {}".format(machine1.hostname))

        await machine1.destroy(force=True)
    finally:
        await model.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)

    loop.run(main())
