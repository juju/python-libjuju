"""
Deploy a charm, wait until it's idle, then destroy the unit and application.

"""
import asyncio
import logging

from juju.model import Model, ModelObserver
from juju.client.connection import Connection


class MyModelObserver(ModelObserver):
    def on_unit_add(self, delta, old, new, model):
        logging.info(
            'New unit added: %s', new.name)

    def on_change(self, delta, old, new, model):
        for unit in model.units.values():
            unit_status = unit.data['agent-status']['current']
            logging.info(
                'Unit %s status: %s', unit.name, unit_status)
            if unit_status == 'idle':
                logging.info(
                    'Destroying unit %s', unit.name)
                loop.create_task(unit.destroy())

    def on_unit_remove(self, delta, old, new, model):
        app_name = old.application
        app = model.applications[app_name]
        if not app.units:
            logging.info(
                'Destroying application %s', app.name)
            loop.create_task(app.destroy())


async def run():
    conn = await Connection.connect_current()
    model = Model(conn)
    model.add_observer(MyModelObserver())
    await model.deploy(
        'ubuntu-0',
        service_name='ubuntu',
        series='trusty',
        channel='stable',
    )
    await model.watch()


logging.basicConfig(level=logging.INFO)
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
