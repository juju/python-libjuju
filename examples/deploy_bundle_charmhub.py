# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
This example:
1. Connects to the current model
2. Deploy a bundle from charmhub and waits until it reports itself active
3. Destroys the unit and application
"""
from juju import jasyncio
from juju.model import Model


async def main():
    model = Model()
    print("Connecting to model")
    # connect to current model with current user, per Juju CLI
    await model.connect()

    try:
        print("Deploying lma-light")
        applications = await model.deploy("ch:lma-light", channel="edge", trust=True)

        print("Waiting for active")
        await model.wait_for_idle(status="active")

        print("Removing lma-light")
        for application in applications:
            await application.remove()
    finally:
        print("Disconnecting from model")
        await model.disconnect()


if __name__ == "__main__":
    jasyncio.run(main())
