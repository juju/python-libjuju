import uuid

import pytest

from juju.controller import Controller

from ..base import bootstrapped

MB = 1
GB = 1024


class CleanModel():
    def __init__(self):
        self.controller = None
        self.model = None

    async def __aenter__(self):
        self.controller = Controller()
        await self.controller.connect_current()

        model_name = 'model-{}'.format(uuid.uuid4())
        self.model = await self.controller.add_model(model_name)

        return self.model

    async def __aexit__(self, exc_type, exc, tb):
        await self.model.disconnect()
        await self.controller.destroy_model(self.model.info.uuid)
        await self.controller.disconnect()


@bootstrapped
@pytest.mark.asyncio
async def test_add_machine(event_loop):
    from juju.machine import Machine

    async with CleanModel() as model:
        # add a new default machine
        machine1 = await model.add_machine()

        # add a machine with constraints, disks, and series
        machine2 = await model.add_machine(
            constraints={
                'mem': 256 * MB,
            },
            disks=[{
                'pool': 'rootfs',
                'size': 10 * GB,
                'count': 1,
            }],
            series='xenial',
        )

        # add a lxd container to machine2
        machine3 = await model.add_machine(
            'lxd:{}'.format(machine2.id))

        for m in (machine1, machine2, machine3):
            assert isinstance(m, Machine)

        assert len(model.machines) == 3
