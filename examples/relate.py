"""
Deploy two charms and relate them.

"""
import asyncio
import logging

from juju.model import Model, ModelObserver


class MyModelObserver(ModelObserver):
    def on_change(self, delta, old, new, model):
        if model.all_units_idle():
            logging.debug('All units idle, disconnecting')
            task = model.loop.create_task(model.disconnect())
            task.add_done_callback(lambda fut: model.loop.stop())


async def run():
    model = Model()
    await model.connect_current()

    await model.reset(force=True)
    await model.block_until(
        lambda: len(model.machines) == 0
    )
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
loop.create_task(run())
loop.run_forever()
