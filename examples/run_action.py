# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from juju import jasyncio
from juju.model import Model

# logging.basicConfig(level='DEBUG')

# Get a k8s controller
# e.g. juju bootstrap microk8s test-k8s

# Add a model
# e.g. juju add-model test-actions

# Then run this module
# e.g. python examples/run_action.py


async def _get_password():
    model = Model()
    await model.connect()
    await model.deploy('zinc-k8s')
    await model.wait_for_idle(status="active")

    unit = model.applications['zinc-k8s'].units[0]
    action1 = await unit.run_action("get-admin-password")
    assert action1.status == 'pending'

    action2 = await action1.wait()
    assert action2.status == 'completed'

    print(action2.results["admin-password"])

    # They are the same object
    assert action1 is action2

    await model.disconnect()


if __name__ == "__main__":
    jasyncio.run(_get_password())
