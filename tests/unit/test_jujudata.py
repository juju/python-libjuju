import unittest
import os
import contextlib

from juju.client.jujudata import FileJujuData, NoModelException
from juju.errors import JujuError


def yamls():
    return {
        'controllers.yaml': {
            'current-controller': 'test-controller',
            'controllers': {
                'test-controller': {
                    'uuid': 'a78b712e99abc9',
                    'api-endpoints': '10.10.10.1:17017',
                    'ca-cert': 'somecert',
                },
                'other-controller': {},
            }
        },
        'accounts.yaml': {
            'controllers': {
                'test-controller': {
                    'user': 'test-user',
                    'password': 'pwd',
                },
                'other-controller': {
                    'user': 'other-user',
                    'password': 'pwd',
                },
                'no-user-controller': {},
            }
        },
        'models.yaml': {
            'controllers': {
                'test-controller': {
                    'current-model': 'test-model'
                },
                'other-controller': {}
            }
        },
    }


@contextlib.contextmanager
def set_env_juju_model():
    os.environ['JUJU_MODEL'] = 'env-model'
    yield
    os.environ.pop('JUJU_MODEL')


class BaseTestJujuDataParseModel:
    def _jujudata(self):
        jjdata = FileJujuData()
        jjdata._loaded = yamls()
        return jjdata

    def _parse_model(self, model):
        data = self._jujudata()
        return data.parse_model(model)

    def test_implicit_controller_name(self):
        controller_name, model_name = self._parse_model('test-model')
        assert controller_name == 'test-controller'
        assert model_name == 'test-user/test-model'

    def test_unknown_model_name(self):
        controller_name, model_name = self._parse_model('some-model')
        assert controller_name == 'test-controller'
        assert model_name == 'test-user/some-model'

    def test_explicit_current_controller_name(self):
        controller_name, model_name = self._parse_model('test-controller:test-model')
        assert controller_name == 'test-controller'
        assert model_name == 'test-user/test-model'

    def test_explicit_user_name(self):
        controller_name, model_name = self._parse_model('test-controller:some-user/test-model')
        assert controller_name == 'test-controller'
        assert model_name == 'some-user/test-model'

    def test_explicit_other_controller_name(self):
        controller_name, model_name = self._parse_model('other-controller:test-model')
        assert controller_name == 'other-controller'
        assert model_name == 'other-user/test-model'

    def test_explicit_unknown_controller_name_raises(self):
        with self.assertRaises(JujuError):
            self._parse_model('unknown-controller:test-model')

    def test_explicit_controller_name_no_account_raises(self):
        with self.assertRaises(JujuError):
            self._parse_model('no-user-controller:test-model')

    def test_implicit_controller_no_model_raises(self):
        data = self._jujudata()
        data._loaded['controllers.yaml']['current-controller'] = 'other-controller'
        with self.assertRaises(NoModelException):
            # other-controller does not have a model
            data.parse_model(None)


class TestJujuDataParseModelWithoutEnvVariable(unittest.TestCase, BaseTestJujuDataParseModel):
    def test_no_args_current_model(self):
        controller_name, model_name = self._parse_model(None)
        assert controller_name == 'test-controller'
        assert model_name == 'test-user/test-model'


class TestJujuDataParseModelWithEnvVariable(unittest.TestCase, BaseTestJujuDataParseModel):
    def _parse_model(self, model):
        data = self._jujudata()
        with set_env_juju_model():
            return data.parse_model(model)

    def test_no_args_env_model(self):
        controller_name, model_name = self._parse_model(None)
        assert controller_name == 'test-controller'
        assert model_name == 'test-user/env-model'
