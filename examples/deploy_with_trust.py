"""
This example:

1. Connects to the current model
2. Deploy a bundle with trust and waits until it reports itself active
3. Destroys the unit and application

"""
from juju import loop
from juju.model import Model


async def main():
    model = Model()
    print('Connecting to model')
    # connect to current model with current user, per Juju CLI
    await model.connect()

    try:
        print('Deploying trusted bundle')
        applications = await model.deploy(
            'cs:~juju-qa/bundle/aws-integrator-trust-single-1',
            series='xenial',
            channel='beta',
            trust=True,
        )
        print("apps {}".format(applications))

        print('Waiting for active')
        await model.block_until(
            lambda: all(unit.workload_status == 'active'
                        for application in applications
                            for unit in application.units))

        print('Removing bundle')
        await (application.remove() for application in applications)
    finally:
        print('Disconnecting from model')
        await model.disconnect()


if __name__ == '__main__':
    loop.run(main())
