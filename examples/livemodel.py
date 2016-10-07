"""
This example:

1. Connects to the current model
2. Watches the model and prints all changes
3. Runs forever (kill with Ctrl-C)

"""
import asyncio

from juju.model import Model


async def on_model_change(delta, old, new, model):
    print(delta.entity, delta.type, delta.data)
    print(old)
    print(new)
    print(model)


async def watch_model():
    model = Model()
    await model.connect_current()

    model.add_observer(on_model_change)


loop = asyncio.get_event_loop()
loop.create_task(watch_model())
loop.run_forever()
