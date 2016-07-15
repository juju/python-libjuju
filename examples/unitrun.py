"""
Run this one against a model that has at least one unit deployed.

"""
import asyncio
import functools

from juju.model import Model
from juju.unit import Unit
from juju.client.connection import Connection


loop = asyncio.get_event_loop()
conn = loop.run_until_complete(Connection.connect_current())

_seen_units = set()


async def run_stuff_on_unit(unit):
    if unit.name in _seen_units:
        return

    print('Running command on unit', unit.name)
    # unit.run() returns a client.ActionResults instance
    action_results = await unit.run('unit-get public-address')
    _seen_units.add(unit.name)
    action_result = action_results.results[0]

    print('Results from unit', unit.name)
    print(action_result.__dict__)


def on_model_change(delta, old, new, model):
    if isinstance(new, Unit):
        task = loop.create_task(run_stuff_on_unit(new))

    if delta.entity == 'action':
        print(delta.data)
        print(new)


async def watch_model():
    model = Model(conn)
    model.add_observer(on_model_change)
    await model.watch()

loop.run_until_complete(watch_model())
