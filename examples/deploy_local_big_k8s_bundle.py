# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
This example:

1. Connects to the current model
2. Deploy a bundle and waits until it reports itself active
3. Destroys the units and applications

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
        await model.deploy(
            './examples/k8s-local-bundle/big-k8s-bundle.yaml',
            channel='edge',
            trust=True,
        )
    finally:
        print('Disconnecting from model')
        await model.disconnect()
        print("Success")


if __name__ == '__main__':
    jasyncio.run(main())
