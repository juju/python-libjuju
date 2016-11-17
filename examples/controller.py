"""
This example:

1. Connects to current controller.
2. Creates a new model.
3. Deploys an application on the new model.

"""
import asyncio
import logging

from juju.model import Model, ModelObserver
from juju.controller import Controller


class MyModelObserver(ModelObserver):
    async def on_change(self, delta, old, new, model):
        pass


async def run():
    controller = Controller()
    await controller.connect_current()
    model = await controller.add_model(
        'libjuju-test',
        'cloud-aws',
        'cloudcred-aws_tvansteenburgh@external_aws-tim',
    )
    await model.deploy(
        'ubuntu-0',
        service_name='ubuntu',
        series='trusty',
        channel='stable',
    )
    await model.disconnect()
    await controller.disconnect()
    model.loop.stop()


logging.basicConfig(level=logging.DEBUG)
ws_logger = logging.getLogger('websockets.protocol')
ws_logger.setLevel(logging.INFO)
loop = asyncio.get_event_loop()
loop.set_debug(False)
loop.create_task(run())
loop.run_forever()
