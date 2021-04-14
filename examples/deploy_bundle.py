"""
This example:

1. Connects to the current model
2. Deploy a bundle and waits until it reports itself active
3. Destroys the units and applications

"""
from juju.controller import Controller
from juju import loop


async def main():
    controller = Controller()
    # connect to current controller with current user, per Juju CLI
    await controller.connect()

    bundles = [('cs:~juju-qa/bundle/basic-0', 'beta'), ('juju-qa-bundle-test', None)]
    for i in range(len(bundles)): 
        deployment = bundles[i]
        model = await controller.add_model('model{}'.format(i))

        try:
            print('Deploying bundle')
            applications = await model.deploy(
                deployment[0],
                channel=deployment[1],
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

    await controller.disconnect()


if __name__ == '__main__':
    loop.run(main())
