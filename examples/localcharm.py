"""
This example shows how to deploy a local charm. It:

1. Connects to current model.
2. Uploads a local charm (directory on filesystem) to the model.
3. Deploys the uploaded charm.

"""
import logging

from juju import jasyncio
from juju.model import Model


async def main():
    model = Model()
    await model.connect()

    # Deploy a local charm using a path to the charm directory
    await model.deploy(
        './charms/ubuntu',
        application_name='ubuntu',
        series='trusty',
    )

    await model.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)
    jasyncio.run(main())
