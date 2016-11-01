"""
This example:

1. Connects to the current model
2. Resets it
3. Deploys a charm and prints its config and constraints

"""
import asyncio
import logging

from juju.model import Model


async def run():
    model = Model()
    await model.connect_current()
    await model.reset(force=True)

    ubuntu_app = await model.deploy(
        'mysql',
        service_name='mysql',
        series='trusty',
        channel='stable',
        constraints={
            'mem': 512 * 1024 * 1024
        },
    )
    print(await ubuntu_app.get_config())
    print(await ubuntu_app.get_constraints())

    await model.disconnect()
    model.loop.stop()

logging.basicConfig(level=logging.DEBUG)
ws_logger = logging.getLogger('websockets.protocol')
ws_logger.setLevel(logging.INFO)
loop = asyncio.get_event_loop()
loop.set_debug(False)
loop.create_task(run())
loop.run_forever()
