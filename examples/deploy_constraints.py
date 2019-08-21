"""
This example:

1. Connects to the current controller
2. Adds a model to the controller
3. Attempts to deploy a charm with constraints

"""
from juju import loop
from juju.controller import Controller


async def main():
    controller = Controller()
    await controller.connect()

    try:
        model = await controller.add_model("test-model")
        application = await model.deploy("ubuntu", constraints={"arch": "amd64"})

        print('Waiting for active')
        await model.block_until(
            lambda: all(unit.workload_status == 'active'
                        for unit in application.units))
        print("Successfully deployed!")
        print('Removing bundle')
        await application.remove()
    finally:
        print('Disconnecting from controller')
        await controller.disconnect()
        print("Success")


if __name__ == '__main__':
    loop.run(main())
