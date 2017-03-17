"""
This example:

1. Connects to current controller.
2. Creates a new model.
3. Deploys an application on the new model.
4. Disconnects from the model
5. Destroys the model

"""
import asyncio
import logging

from juju.controller import Controller
from juju import loop


async def main():
    controller = Controller()
    await controller.connect_current()
    model = await controller.add_model(
        'my-test-model',
        'aws',
        'aws-tim',
    )
    await model.deploy(
        'ubuntu-0',
        application_name='ubuntu',
        series='trusty',
        channel='stable',
    )
    await model.disconnect()
    await controller.destroy_model(model.info.uuid)
    await controller.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)
    loop.run(main())
