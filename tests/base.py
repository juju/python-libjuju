import inspect
import subprocess
import uuid
from contextlib import contextmanager
from pathlib import Path

import mock

import pytest
from juju.client.jujudata import FileJujuData
from juju.controller import Controller


def is_bootstrapped():
    try:
        result = subprocess.run(['juju', 'switch'], stdout=subprocess.PIPE)
        return (
            result.returncode == 0 and
            len(result.stdout.decode().strip()) > 0)
    except FileNotFoundError:
        return False


bootstrapped = pytest.mark.skipif(
    not is_bootstrapped(),
    reason='bootstrapped Juju environment required')

test_run_nonce = uuid.uuid4().hex[-4:]


class CleanController():
    """
    Context manager that automatically connects and disconnects from
    the currently active controller.

    Note: Unlike CleanModel, this will not create a new controller for you,
    and an active controller must already be available.
    """
    def __init__(self):
        self._controller = None

    async def __aenter__(self):
        self._controller = Controller()
        await self._controller.connect()
        return self._controller

    async def __aexit__(self, exc_type, exc, tb):
        await self._controller.disconnect()


class CleanModel():
    """
    Context manager that automatically connects to the currently active
    controller, adds a fresh model, returns the connection to that model,
    and automatically disconnects and cleans up the model.

    The new model is also set as the current default for the controller
    connection.
    """
    def __init__(self, bakery_client=None):
        self._controller = None
        self._model = None
        self._model_uuid = None
        self._bakery_client = bakery_client

    async def __aenter__(self):
        model_nonce = uuid.uuid4().hex[-4:]
        frame = inspect.stack()[1]
        test_name = frame.function.replace('_', '-')
        jujudata = TestJujuData()
        self._controller = Controller(
            jujudata=jujudata,
            bakery_client=self._bakery_client,
        )
        controller_name = jujudata.current_controller()
        user_name = jujudata.accounts()[controller_name]['user']
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
        jujudata.set_model(
            controller_name,
            user_name + "/" + model_name,
            self._model.info.uuid,
        )

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

    def set_model(self, controller_name, model_name, model_uuid):
        self.__controller_name = controller_name
        self.__model_name = model_name
        self.__model_uuid = model_uuid

    def current_model(self, *args, **kwargs):
        return self.__model_name or super().current_model(*args, **kwargs)

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


@contextmanager
def patch_file(filename):
    """
    "Patch" a file so that its current contents are automatically restored
    when the context is exited.
    """
    filepath = Path(filename).expanduser()
    data = filepath.read_bytes()
    try:
        yield
    finally:
        filepath.write_bytes(data)
