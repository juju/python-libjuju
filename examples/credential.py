import sys
from juju import loop
from juju.controller import Controller


async def main(cloud_name, credential_name):
    controller = Controller()
    model = None
    print('Connecting to controller')
    # connect to current controller with current user, per Juju CLI
    await controller.connect()
    try:
        print('Adding model')
        model = await controller.add_model(
            'test',
            cloud_name=cloud_name,
            credential_name=credential_name)

        # verify credential
        print("Verify model's credential: {}".format(
            model.info.cloud_credential_tag))

        # verify we can deploy
        print('Deploying ubuntu')
        app = await model.deploy('ubuntu-10')

        print('Waiting for active')
        await model.block_until(
            lambda: app.units and all(unit.workload_status == 'active'
                                      for unit in app.units))

        print('Removing ubuntu')
        await app.remove()
    finally:
        print('Cleaning up')
        if model:
            print('Removing model')
            model_uuid = model.info.uuid
            await model.disconnect()
            await controller.destroy_model(model_uuid)
        print('Disconnecting')
        await controller.disconnect()


if __name__ == '__main__':
    assert len(sys.argv) > 2, 'Please provide a cloud and credential name'
    loop.run(main(sys.argv[1], sys.argv[2]))
