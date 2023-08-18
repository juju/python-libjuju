# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
This example:

1. Connects to the current model
2. Deploy a bundle and waits until it reports itself active
3. Destroys the units and applications

"""
from juju.controller import Controller
from juju import jasyncio


async def main():
    controller = Controller()
    # connect to current controller with current user, per Juju CLI
    await controller.connect()

    # Deploy charmhub bundle
    await deploy_bundle(controller, 'juju-qa-bundle-test')

    await controller.disconnect()


async def deploy_bundle(controller, url, channel=None):
    models = await controller.list_models()
    model = await controller.add_model('model{}'.format(len(models) + 1))

    try:
        print('Deploying bundle')

        applications = await deploy_and_wait_for_bundle(model, url, channel)

        print("Successfully deployed!")
        print('Removing bundle')
        for application in applications:
            await application.remove()
    finally:
        print('Disconnecting from model')
        await model.disconnect()
        print("Success")


async def deploy_and_wait_for_bundle(model, url, channel=None):
    applications = await model.deploy(url, channel=channel)

    print('Waiting for active')
    await model.block_until(
        lambda: all(unit.workload_status == 'active'
                    for application in applications for unit in application.units))

    return applications

if __name__ == '__main__':
    jasyncio.run(main())
