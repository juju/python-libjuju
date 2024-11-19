# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""This example:

1. Creates a model on the current controller
2. Deploys a charm to it.
3. Attempts to ssh into the charm

"""

import asyncio
import uuid
from logging import getLogger

from juju import jasyncio, utils
from juju.controller import Controller

LOG = getLogger(__name__)


async def main():
    controller = Controller()
    print("Connecting to controller")
    # connect to current controller with current user, per Juju CLI
    await controller.connect()

    try:
        model_name = f"addmodeltest-{uuid.uuid4()}"
        print(f"Adding model {model_name}")
        model = await controller.add_model(model_name)

        print("Deploying ubuntu")
        application = await model.deploy(
            "ch:ubuntu",
            application_name="ubuntu",
            series="jammy",
            channel="stable",
        )

        print("Waiting for active")
        await asyncio.sleep(10)
        await model.wait_for_idle(status="active")

        print("Verifying that we can ssh into the created model")
        ret = await utils.execute_process(
            "juju", "ssh", "-m", model_name, "ubuntu/0", "ls /", log=LOG
        )
        assert ret

        print("Removing ubuntu")
        await application.remove()

        print("Destroying model")
        await controller.destroy_model(model.info.uuid)

    except Exception:
        LOG.exception(f"Test failed! Model {model_name} may not be cleaned up")

    finally:
        print("Disconnecting from controller")
        if model:
            await model.disconnect()
        await controller.disconnect()


if __name__ == "__main__":
    jasyncio.run(main())
