"""
This example shows how to deploy a local charm. It:

1. Connects to current model.
2. Uploads a local charm (directory on filesystem) to the model.
3. Deploys the uploaded charm.

"""
import asyncio
import logging

from juju.model import Model


async def run():
    model = Model()
    await model.connect_current()

    # Upload local charm to the model.
    # The returned 'local:' url can be used to deploy the charm.
    charm_url = await model.add_local_charm_dir(
        '/home/tvansteenburgh/src/charms/ubuntu', 'trusty')

    # Deploy the charm using the 'local:' charm.
    await model.deploy(
        charm_url,
        application_name='ubuntu',
    )

    await model.disconnect()
    model.loop.stop()


logging.basicConfig(level=logging.DEBUG)
ws_logger = logging.getLogger('websockets.protocol')
ws_logger.setLevel(logging.INFO)
loop = asyncio.get_event_loop()
loop.set_debug(False)
loop.create_task(run())
loop.run_forever()
