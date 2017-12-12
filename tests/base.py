import inspect
import subprocess
import uuid

import mock
from juju.client.jujudata import FileJujuData
from juju.controller import Controller

import pytest


def is_bootstrapped():
    result = subprocess.run(['juju', 'switch'], stdout=subprocess.PIPE)
    return (
        result.returncode == 0 and
        len(result.stdout.decode().strip()) > 0)


bootstrapped = pytest.mark.skipif(
    not is_bootstrapped(),
    reason='bootstrapped Juju environment required')

test_run_nonce = uuid.uuid4().hex[-4:]


class CleanController():
    def __init__(self):
        self._controller = None

    async def __aenter__(self):
        self._controller = Controller()
        await self._controller.connect()
        return self._controller

    async def __aexit__(self, exc_type, exc, tb):
        await self._controller.disconnect()


class CleanModel():
    def __init__(self):
        self._controller = None
        self._model = None
        self._model_uuid = None

    async def __aenter__(self):
        model_nonce = uuid.uuid4().hex[-4:]
        frame = inspect.stack()[1]
        test_name = frame.function.replace('_', '-')
        self._controller = Controller()
        juju_data = TestJujuData()
        controller_name = juju_data.current_controller()
        user_name = juju_data.accounts()[controller_name]['user']
        await self._controller.connect(controller_name)

        model_name = 'test-{}-{}-{}'.format(
            test_run_nonce,
            test_name,
            model_nonce,
        )
        self._model = await self._controller.add_model(model_name)

        # Change the JujuData instance so that it will return the new
        # model as the current model name, so that we'll connect
        # to it by default.
        juju_data.__model_name = user_name + "/" + model_name
        juju_data.__controller_name = controller_name
        juju_data.__model_uuid = self._model.info.uuid

        # save the model UUID in case test closes model
        self._model_uuid = self._model.info.uuid

        return self._model

    async def __aexit__(self, exc_type, exc, tb):
        await self._model.disconnect()
        await self._controller.destroy_model(self._model_uuid)
        await self._controller.disconnect()


class TestJujuData(FileJujuData):
    def __init__(self):
        self.__controller_name = None
        self.__model_name = None
        self.__model_uuid = None
        super().__init__()

    def current_model(self):
        return self.__model_name or super().current_model()

    def models(self):
        all_models = super().models()
        if self.__model_name is None:
            return all_models
        all_models.setdefault(self.__controller_name, {})
        all_models[self.__controller_name].setdefault('models', {})
        cmodels = all_models[self.__controller_name]['models']
        cmodels[self.__model_name] = {'uuid': self.__model_uuid}
        return all_models


class AsyncMock(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)
