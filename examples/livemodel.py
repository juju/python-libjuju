"""
This example:

1. Connects to the current model
2. Watches the model and prints all changes
3. Runs forever (kill with Ctrl-C)

"""
from juju.model import Model
from juju import jasyncio


async def on_model_change(delta, old, new, model):
    print(delta.entity, delta.type, delta.data)
    print(old)
    print(new)
    print(model)


async def watch_model():
    model = Model()
    # connect to current model with current user, per Juju CLI
    await model.connect()

    model.add_observer(on_model_change)


if __name__ == '__main__':
    # Run loop until the process is manually stopped (watch_model will loop
    # forever).
    jasyncio.run(watch_model())
