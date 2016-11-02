"""
This example:

1. Connects to current model and resets it.
2. Deploys one ubuntu unit.
3. Runs an action against the unit.
4. Waits for the action results to come back, then exits.

"""
import asyncio
import logging

from juju.model import Model, ModelObserver

async def run_stuff_on_unit(unit):
    print('Running command on unit', unit.name)

    # unit.run() returns a client.ActionResults instance
    action = await unit.run('unit-get public-address')

    print("Action results: {}".format(action.results))

    # Inform asyncio that we're done.
    await unit.model.disconnect()
    unit.model.loop.stop()


class MyModelObserver(ModelObserver):
    async def on_unit_add(self, delta, old, new, model):
        loop.create_task(run_stuff_on_unit(new))


async def run():
    model = Model()
    await model.connect_current()
    await model.reset(force=True)
    model.add_observer(MyModelObserver())

    await model.deploy(
        'ubuntu-0',
        service_name='ubuntu',
        series='trusty',
        channel='stable',
    )


logging.basicConfig(level=logging.DEBUG)
ws_logger = logging.getLogger('websockets.protocol')
ws_logger.setLevel(logging.INFO)
loop = asyncio.get_event_loop()
loop.set_debug(False)
loop.create_task(run())
loop.run_forever()
