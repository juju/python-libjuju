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
        self.user_name = None
        self.controller = None
        self.controller_name = None
        self.model = None
        self.model_name = None
        self.model_uuid = None

    async def __aenter__(self):
        self.controller = Controller()
        juju_data = JujuData()
        self.controller_name = juju_data.current_controller()
        self.user_name = juju_data.accounts()[self.controller_name]['user']
        await self.controller.connect_controller(self.controller_name)

        self.model_name = 'test-{}'.format(uuid.uuid4())
        self.model = await self.controller.add_model(self.model_name)

        # save the model UUID in case test closes model
        self.model_uuid = self.model.info.uuid

        # Ensure that we connect to the new model by default.  This also
        # prevents failures if test was started with no current model.
        self._patch_cm = mock.patch.object(JujuData, 'current_model',
                                           return_value=self.model_name)
        self._patch_cm.start()

        # Ensure that the models data includes this model, since it doesn't
        # get added to the client store by Controller.add_model().
        self._orig_models = JujuData().models
        self._patch_models = mock.patch.object(JujuData, 'models',
                                               side_effect=self._models)
        self._patch_models.start()

        return self.model

    def _models(self):
        result = self._orig_models()
        models = result[self.controller_name]['models']
        full_model_name = '{}/{}'.format(self.user_name, self.model_name)
        if full_model_name not in models:
            models[full_model_name] = {'uuid': self.model_uuid}
        return result

    async def __aexit__(self, exc_type, exc, tb):
        self._patch_models.stop()
        self._patch_cm.stop()
        await self.model.disconnect()
        await self.controller.destroy_model(self.model_uuid)
        await self.controller.disconnect()


class AsyncMock(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)
