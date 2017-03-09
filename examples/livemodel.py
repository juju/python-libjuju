"""
This example:

1. Connects to the current model
2. Watches the model and prints all changes
3. Runs forever (kill with Ctrl-C)

"""
import asyncio

from juju.model import Model
from juju import loop


async def on_model_change(delta, old, new, model):
    print(delta.entity, delta.type, delta.data)
    print(old)
    print(new)
    print(model)


async def watch_model():
    model = Model()
    await model.connect_current()

    model.add_observer(on_model_change)


if __name__ == '__main__':
    # Run loop until the process is manually stopped (watch_model will loop
    # forever).
    loop.run(watch_model())
