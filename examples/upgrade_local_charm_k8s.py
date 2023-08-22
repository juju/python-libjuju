# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
This example:

1. Connects to the current model
2. Deploy a bundle and waits until it reports itself active
3. Upgrades the charm with a local path
4. Destroys the units and applications

"""
from juju import jasyncio
from juju.model import Model


async def main():
    model = Model()
    print('Connecting to model')
    # Connect to current model with current user, per Juju CLI
    await model.connect()

    try:
        print('Deploying bundle')
        applications = await model.deploy(
            './examples/k8s-local-bundle/bundle.yaml',
        )

        print('Waiting for active')
        await model.wait_for_idle(status='active')
        print("Successfully deployed!")

        local_path = './examples/charms/onos.charm'
        print('Upgrading charm with %s' % local_path)
        await applications[0].upgrade_charm(path=local_path)

        await model.wait_for_idle(status='active')

        print('Removing bundle')
        for application in applications:
            await application.remove()
    finally:
        print('Disconnecting from model')
        await model.disconnect()
        print("Success")


if __name__ == '__main__':
    jasyncio.run(main())
