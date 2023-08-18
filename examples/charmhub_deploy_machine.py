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
            application_name='juju-qa-test',
            channel='2.0/edge',
        )

        print('Waiting for active')
        await model.block_until(
            lambda: all(unit.workload_status == 'active'
                        for unit in application.units))

    finally:
        print('Disconnecting from model')
        await model.disconnect()

if __name__ == '__main__':
    jasyncio.run(main())
