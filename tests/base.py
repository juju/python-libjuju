import mock
import subprocess
import uuid

import pytest

from juju.controller import Controller
from juju.client.connection import JujuData


def is_bootstrapped():
    result = subprocess.run(['juju', 'switch'], stdout=subprocess.PIPE)
    return (
        result.returncode == 0 and
        len(result.stdout.decode().strip()) > 0)

bootstrapped = pytest.mark.skipif(
    not is_bootstrapped(),
    reason='bootstrapped Juju environment required')


class CleanController():
    def __init__(self):
        self.controller = None

    async def __aenter__(self):
        self.controller = Controller()
        await self.controller.connect_current()
        return self.controller

    async def __aexit__(self, exc_type, exc, tb):
        await self.controller.disconnect()


class CleanModel():
    def __init__(self):
        self.controller = None
        self.model = None

    async def __aenter__(self):
        self.controller = Controller()
        await self.controller.connect_current()

        model_name = 'model-{}'.format(uuid.uuid4())
        self.model = await self.controller.add_model(model_name)

        # save the model UUID in case test closes model
        self.model_uuid = self.model.info.uuid

        # Ensure that we connect to the new model by default.  This also
        # prevents failures if test was started with no current model.
        self._patch_cm = mock.patch.object(JujuData, 'current_model',
                                           return_value=model_name)
        self._patch_cm.start()

        return self.model

    async def __aexit__(self, exc_type, exc, tb):
        self._patch_cm.stop()
        await self.model.disconnect()
        await self.controller.destroy_model(self.model_uuid)
        await self.controller.disconnect()


class AsyncMock(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)
