"""
This example:

1. Connects to the current model
2. Deploy a charm and waits until it reports itself active
3. Destroys the unit and application

"""
from juju import loop
from juju.model import Model


async def main():
    model = Model()
    print('Connecting to model')
    await model.connect()

    try:
        print('Deploying ')
        application = await model.deploy(
            'ch:snappass-test',
            application_name='snappass'
        )

        print('Waiting for active')
        await model.block_until(
            lambda: all(unit.workload_status == 'active'
                        for unit in application.units))

    finally:
        print('Disconnecting from model')
        await model.disconnect()

if __name__ == '__main__':
    loop.run(main())
