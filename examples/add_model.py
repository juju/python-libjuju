"""
This example:

1. Creates a model on the current controller
2. Deploys a charm to it.
3. Attempts to ssh into the charm

"""
from juju import jasyncio
from juju import utils
from juju.controller import Controller
import asyncio
from logging import getLogger
import uuid

LOG = getLogger(__name__)


async def main():
    controller = Controller()
    print("Connecting to controller")
    # connect to current controller with current user, per Juju CLI
    await controller.connect()

    try:
        model_name = "addmodeltest-{}".format(uuid.uuid4())
        print("Adding model {}".format(model_name))
        model = await controller.add_model(model_name)

        print('Deploying ubuntu')
        application = await model.deploy(
            'ch:ubuntu',
            application_name='ubuntu',
            series='jammy',
            channel='stable',
        )

        print('Waiting for active')
        await asyncio.sleep(10)
        await model.wait_for_idle(status='active')

        print("Verifying that we can ssh into the created model")
        ret = await utils.execute_process(
            'juju', 'ssh', '-m', model_name, 'ubuntu/0', 'ls /', log=LOG)
        assert ret

        print('Removing ubuntu')
        await application.remove()

        print("Destroying model")
        await controller.destroy_model(model.info.uuid)

    except Exception:
        LOG.exception(
            "Test failed! Model {} may not be cleaned up".format(model_name))

    finally:
        print('Disconnecting from controller')
        if model:
            await model.disconnect()
        await controller.disconnect()


if __name__ == '__main__':
    jasyncio.run(main())
