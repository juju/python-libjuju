"""
This example:

1. Connects to the current model
2. Deploy a bundle with trust and waits until it reports itself active
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
        print('Deploying trusted bundle application ubuntu')
        applications = await model.deploy(
            'cs:~juju-qa/bundle/basic-trusted-1',
            channel='beta',
            trust=True,
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


if __name__ == '__main__':
    loop.run(main())
