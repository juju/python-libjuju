import asyncio

from juju.model import Model
from juju.client.connection import Connection


loop = asyncio.get_event_loop()
conn = loop.run_until_complete(Connection.connect_current())


def on_model_change(delta, old, new, model):
    print(delta.entity, delta.type, delta.data)
    print(old)
    print(new)
    print(model)

async def watch_model():
    model = Model(conn)
    model.add_observer(on_model_change)
    await model.watch()

loop.run_until_complete(watch_model())
