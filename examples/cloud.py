"""
This example:

1. Connects to current controller.
2. Gets the cloud
3. Disconnects from the controller

"""
import logging

from juju import jasyncio
from juju.controller import Controller


async def main():
    controller = Controller()
    await controller.connect()

    await controller.cloud()

    await controller.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)
    jasyncio.run(main())
