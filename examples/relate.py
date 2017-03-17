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
from juju import loop


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
    _shutting_down = False

    async def on_change(self, delta, old, new, model):
        if model.units and model.all_units_idle() and not self._shutting_down:
            self._shutting_down = True
            logging.debug('All units idle, disconnecting')
            await model.reset(force=True)
            await model.disconnect()


async def main():
    model = Model()
    await model.connect_current()

    model.add_observer(MyRemoveObserver())
    await model.reset(force=True)
    model.add_observer(MyModelObserver())

    ubuntu_app = await model.deploy(
        'ubuntu',
        application_name='ubuntu',
        series='trusty',
        channel='stable',
    )
    ubuntu_app.on_change(asyncio.coroutine(
        lambda delta, old_app, new_app, model:
            print('App changed: {}'.format(new_app.entity_id))
    ))
    ubuntu_app.on_remove(asyncio.coroutine(
        lambda delta, old_app, new_app, model:
            print('App removed: {}'.format(old_app.entity_id))
    ))
    ubuntu_app.on_unit_add(asyncio.coroutine(
        lambda delta, old_unit, new_unit, model:
            print('Unit added: {}'.format(new_unit.entity_id))
    ))
    ubuntu_app.on_unit_remove(asyncio.coroutine(
        lambda delta, old_unit, new_unit, model:
            print('Unit removed: {}'.format(old_unit.entity_id))
    ))
    unit_a, unit_b = await ubuntu_app.add_units(count=2)
    unit_a.on_change(asyncio.coroutine(
        lambda delta, old_unit, new_unit, model:
            print('Unit changed: {}'.format(new_unit.entity_id))
    ))
    await model.deploy(
        'nrpe',
        application_name='nrpe',
        series='trusty',
        channel='stable',
        # subordinates must be deployed without units
        num_units=0,
    )
    my_relation = await model.add_relation(
        'ubuntu',
        'nrpe',
    )
    my_relation.on_remove(asyncio.coroutine(
        lambda delta, old_rel, new_rel, model:
            print('Relation removed: {}'.format(old_rel.endpoints))
    ))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)
    loop.run(main())
