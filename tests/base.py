import uuid
import subprocess

import pytest

from juju.controller import Controller


def is_bootstrapped():
    result = subprocess.run(['juju', 'switch'], stdout=subprocess.PIPE)
    return (
        result.returncode == 0 and
        len(result.stdout.decode().strip()) > 0)

bootstrapped = pytest.mark.skipif(
    not is_bootstrapped(),
    reason='bootstrapped Juju environment required')


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
