# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from juju import jasyncio
from juju.model import Model


async def main():
    charm = 'juju-qa-test'

    model = Model()
    print('Connecting to model')
    # connect to current model with current user, per Juju CLI
    await model.connect()

    try:
        print(f'Deploying {charm} --channel 2.0/stable --revision 22')
        application = await model.deploy(
            'juju-qa-test',
            application_name='test',
            channel='2.0/stable',
            revision=22,
        )

        print('Waiting for active')
        await model.wait_for_idle(status='active')

        print(f'Removing {charm}')
        await application.remove()
    finally:
        print('Disconnecting from model')
        await model.disconnect()


if __name__ == '__main__':
    jasyncio.run(main())
