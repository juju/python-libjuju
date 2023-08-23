# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
This example:

1. Connects to the current model
2. Deploy a charm and waits until it reports itself active
3. Destroys the unit and application

"""
from juju import jasyncio
from juju.model import Model


async def main():
    model = Model()
    print('Connecting to model')
    await model.connect()

    try:
        print('Deploying ')
        application = await model.deploy(
            'ch:juju-qa-test',
            application_name='juju-qa-test2',
            channel='2.0/edge',
        )

        print('Waiting for active')
        await model.wait_for_idle(status="active")

        # when run on a container based model it should auto-switch to
        # scale instead of failing with JujuError
        await application.add_unit(count=2)
        await application.destroy()

    finally:
        print('Disconnecting from model')
        await model.disconnect()

if __name__ == '__main__':
    jasyncio.run(main())
