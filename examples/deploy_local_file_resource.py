# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
This example:

1. Connects to the current model
2. Deploy a local charm with a oci-image resource and waits until it reports
   itself active
3. Destroys the unit and application

"""
from juju import jasyncio
from juju.model import Model
from pathlib import Path


async def main():
    model = Model()
    print('Connecting to model')
    # connect to current model with current user, per Juju CLI
    await model.connect()

    application = None
    try:
        print('Deploying local-charm')
        base_dir = Path(__file__).absolute().parent.parent
        charm_path = '{}/tests/integration/file-resource-charm'.format(base_dir)
        resources = {"file-res": "test.file"}
        application = await model.deploy(
            charm_path,
            resources=resources,
        )

        print('Waiting for active')
        await model.wait_for_idle()

        print('Removing Charm')
        await application.remove()
    except Exception as e:
        print(e)
        if application:
            await application.remove()
        await model.disconnect()
    finally:
        print('Disconnecting from model')
        await model.disconnect()


if __name__ == '__main__':
    jasyncio.run(main())
