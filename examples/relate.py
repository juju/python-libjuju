"""
This example:

1. Connects to the current model
2. Resets it
3. Deploys two charms and relates them
4. Waits for units to be idle, then exits

"""
import asyncio
import logging

from juju.model import Model, ModelObserver


class MyRemoveObserver(ModelObserver):
    async def on_change(self, delta, old, new, model):
        if delta.type == 'remove':
            assert(new.latest() == new)
            assert(new.next() is None)
            assert(new.dead)
            assert(new.current)
            assert(new.connected)
            assert(new.previous().dead)
            assert(not new.previous().current)
            assert(not new.previous().connected)


class MyModelObserver(ModelObserver):
    async def on_change(self, delta, old, new, model):
        if model.all_units_idle():
            logging.debug('All units idle, disconnecting')
            await model.disconnect()
            model.loop.stop()


async def run():
    model = Model()
    await model.connect_current()

    model.add_observer(MyRemoveObserver())
    await model.reset(force=True)
    model.add_observer(MyModelObserver())

    await model.deploy(
        'ubuntu-0',
        service_name='ubuntu',
        series='trusty',
        channel='stable',
    )
    await model.deploy(
        'nrpe-11',
        service_name='nrpe',
        series='trusty',
        channel='stable',
        num_units=0,
    )
    await model.add_relation(
        'ubuntu',
        'nrpe',
    )

logging.basicConfig(level=logging.DEBUG)
ws_logger = logging.getLogger('websockets.protocol')
ws_logger.setLevel(logging.INFO)
loop = asyncio.get_event_loop()
loop.set_debug(False)
loop.create_task(run())
loop.run_forever()
