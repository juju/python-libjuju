"""
This example:

1. Connects to the current model
2. Deploy a bundle and waits until it reports itself active
3. Destroys the units and applications

"""
from juju import loop
from juju.model import Model


async def main():
    model = Model()
    print('Connecting to model')
    # Connect to current model with current user, per Juju CLI
    await model.connect()

    try:
        print('Deploying bundle')
        applications = await model.deploy(
            'cs:~juju-qa/bundle/basic-0',
            channel='beta',
        )

        print('Waiting for active')
        await model.block_until(
            lambda: all(unit.workload_status == 'active'
                        for application in applications for unit in application.units))
        print("Successfully deployed!")
        print('Removing bundle')
        for application in applications:
            await application.remove()
    finally:
        print('Disconnecting from model')
        await model.disconnect()
        print("Success")


if __name__ == '__main__':
    loop.run(main())
