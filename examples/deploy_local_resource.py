"""
This example:

1. Connects to the current model
2. Deploy a local charm with a oci-image resource and waits until it reports
   itself active
3. Destroys the unit and application

"""
from juju import loop
from juju.model import Model
from pathlib import Path


async def main():
    model = Model()
    print('Connecting to model')
    # connect to current model with current user, per Juju CLI
    await model.connect()

    try:
        print('Deploying local-charm')
        base_dir = Path(__file__).absolute().parent.parent
        charm_path = '{}/tests/integration/oci-image-charm'.format(base_dir)
        resources = {"oci-image": "ubuntu/latest"}
        application = await model.deploy(
            charm_path,
            resources=resources,
        )

        print('Waiting for active')
        await model.block_until(
            lambda: all(unit.workload_status == 'active'
                        for unit in application.units),
            timeout=120,
        )

        print('Removing Charm')
        await application.remove()
    finally:
        print('Disconnecting from model')
        await model.disconnect()


if __name__ == '__main__':
    loop.run(main())
