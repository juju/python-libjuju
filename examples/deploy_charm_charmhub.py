"""
This example:

1. Connects to the current model
2. Deploy a charm from charmhub and waits until it reports itself active
3. Destroys the unit and application

"""
from juju import loop
from juju.model import Model


async def main():
    model = Model()
    print("Connecting to model")
    # connect to current model with current user, per Juju CLI
    await model.connect()

    try:
        print("Deploying hello-kubecon")
        application = await model.deploy("ch:hello-kubecon")

        print("Waiting for active")
        await model.block_until(
            lambda: all(unit.workload_status == "active" for unit in application.units)
        )

        print("Removing hello-kubecon")
        await application.remove()
    finally:
        print("Disconnecting from model")
        await model.disconnect()


if __name__ == "__main__":
    loop.run(main())
