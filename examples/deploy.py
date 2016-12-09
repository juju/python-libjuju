"""
This example:

1. Connects to the current model
2. Resets it
3. Deploy a charm and waits until it's idle
4. Destroys the unit and application

"""
import asyncio
import logging

from juju.model import Model, ModelObserver


class MyModelObserver(ModelObserver):
    async def on_unit_add(self, delta, old, new, model):
        logging.info(
            'New unit added: %s', new.name)

    async def on_change(self, delta, old, new, model):
        for unit in model.units.values():
            unit_status = unit.data['agent-status']['current']
            logging.info(
                'Unit %s status: %s', unit.name, unit_status)
            if unit_status == 'idle':
                logging.info(
                    'Destroying unit %s', unit.name)
                loop.create_task(unit.destroy())

    async def on_unit_remove(self, delta, old, new, model):
        app_name = old.application
        app = model.applications[app_name]
        if not app.units:
            logging.info(
                'Destroying application %s', app.name)
            loop.create_task(app.destroy())
            await model.block_until(
                lambda: len(model.applications) == 0
            )
            await model.disconnect()
            model.loop.stop()


async def run():
    model = Model()
    await model.connect_current()

    await model.reset(force=True)
    model.add_observer(MyModelObserver())

    await model.deploy(
        'ubuntu-0',
        application_name='ubuntu',
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
