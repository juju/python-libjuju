import unittest

import mock

import asynctest

from juju.client.jujudata import FileJujuData
from juju.model import Model


def _make_delta(entity, type_, data=None):
    from juju.client.client import Delta
    from juju.delta import get_entity_delta

    delta = Delta([entity, type_, data])
    return get_entity_delta(delta)


class TestObserver(unittest.TestCase):
    def _make_observer(self, *args):
        from juju.model import _Observer
        return _Observer(*args)

    def test_cares_about_id(self):
        id_ = 'foo'

        o = self._make_observer(
            None, None, None, id_, None)

        delta = _make_delta(
            'application', 'change', dict(name=id_))

        self.assertTrue(o.cares_about(delta))

    def test_cares_about_type(self):
        type_ = 'application'

        o = self._make_observer(
            None, type_, None, None, None)

        delta = _make_delta(
            type_, 'change', dict(name='foo'))

        self.assertTrue(o.cares_about(delta))

    def test_cares_about_action(self):
        action = 'change'

        o = self._make_observer(
            None, None, action, None, None)

        delta = _make_delta(
            'application', action, dict(name='foo'))

        self.assertTrue(o.cares_about(delta))

    def test_cares_about_predicate(self):
        def predicate(delta):
            return delta.data.get('fizz') == 'bang'

        o = self._make_observer(
            None, None, None, None, predicate)

        delta = _make_delta(
            'application', 'change', dict(fizz='bang'))

        self.assertTrue(o.cares_about(delta))


class TestModelState(unittest.TestCase):
    def test_apply_delta(self):
        from juju.model import Model
        from juju.application import Application

        model = Model()
        model._connector = mock.MagicMock()
        delta = _make_delta('application', 'add', dict(name='foo'))

        # test add
        prev, new = model.state.apply_delta(delta)
        self.assertEqual(
            len(model.state.state[delta.entity][delta.get_id()]), 1)
        self.assertIsNone(prev)
        self.assertIsInstance(new, Application)

        # test remove
        delta.type = 'remove'
        prev, new = model.state.apply_delta(delta)
        # length of the entity history deque is now 3:
        # - 1 for the first delta
        # - 1 for the second delta
        # - 1 for the None sentinel appended after the 'remove'
        self.assertEqual(
            len(model.state.state[delta.entity][delta.get_id()]), 3)
        self.assertIsInstance(new, Application)
        # new object is falsy because its data is None
        self.assertFalse(new)
        self.assertIsInstance(prev, Application)
        self.assertTrue(prev)


def test_get_series():
    from juju.model import Model
    model = Model()
    entity = {
        'Meta': {
            'supported-series': {
                'SupportedSeries': [
                    'xenial',
                    'trusty',
                ],
            },
        },
    }
    assert model._get_series('cs:trusty/ubuntu', entity) == 'trusty'
    assert model._get_series('xenial/ubuntu', entity) == 'xenial'
    assert model._get_series('~foo/xenial/ubuntu', entity) == 'xenial'
    assert model._get_series('~foo/ubuntu', entity) == 'xenial'
    assert model._get_series('ubuntu', entity) == 'xenial'
    assert model._get_series('cs:ubuntu', entity) == 'xenial'


class TestContextManager(asynctest.TestCase):
    @asynctest.patch('juju.model.Model.disconnect')
    @asynctest.patch('juju.model.Model.connect')
    async def test_normal_use(self, mock_connect, mock_disconnect):
        from juju.model import Model

        async with Model() as model:
            self.assertTrue(isinstance(model, Model))

        self.assertTrue(mock_connect.called)
        self.assertTrue(mock_disconnect.called)

    @asynctest.patch('juju.model.Model.disconnect')
    @asynctest.patch('juju.model.Model.connect')
    async def test_exception(self, mock_connect, mock_disconnect):
        from juju.model import Model

        class SomeException(Exception):
            pass

        with self.assertRaises(SomeException):
            async with Model():
                raise SomeException()

        self.assertTrue(mock_connect.called)
        self.assertTrue(mock_disconnect.called)

    async def test_no_current_connection(self):
        from juju.model import Model
        from juju.errors import JujuConnectionError

        class NoControllerJujuData(FileJujuData):
            def current_controller(self):
                return ""

        with self.assertRaises(JujuConnectionError):
            async with Model(jujudata=NoControllerJujuData()):
                pass


@asynctest.patch('juju.model.Model._after_connect')
class TestModelConnect(asynctest.TestCase):
    @asynctest.patch('juju.client.connector.Connector.connect_model')
    async def test_no_args(self, mock_connect_model, _):
        m = Model()
        await m.connect()
        mock_connect_model.assert_called_once_with(None)

    @asynctest.patch('juju.client.connector.Connector.connect_model')
    async def test_with_model_name(self, mock_connect_model, _):
        m = Model()
        await m.connect(model_name='foo')
        mock_connect_model.assert_called_once_with('foo')

    @asynctest.patch('juju.client.connector.Connector.connect_model')
    async def test_with_endpoint_but_no_uuid(self, mock_connect_model, _):
        m = Model()
        with self.assertRaises(TypeError):
            await m.connect(endpoint='0.1.2.3:4566')
        self.assertEqual(mock_connect_model.call_count, 0)

    @asynctest.patch('juju.client.connector.Connector.connect')
    async def test_with_endpoint_and_uuid_no_auth(self, mock_connect, _):
        m = Model()
        with self.assertRaises(TypeError):
            await m.connect(endpoint='0.1.2.3:4566', uuid='some-uuid')
        self.assertEqual(mock_connect.call_count, 0)

    @asynctest.patch('juju.client.connector.Connector.connect')
    async def test_with_endpoint_and_uuid_with_userpass(self, mock_connect, _):
        m = Model()
        with self.assertRaises(TypeError):
            await m.connect(endpoint='0.1.2.3:4566',
                            uuid='some-uuid',
                            username='user')
        await m.connect(endpoint='0.1.2.3:4566',
                        uuid='some-uuid',
                        username='user',
                        password='pass')
        mock_connect.assert_called_once_with(endpoint='0.1.2.3:4566',
                                             uuid='some-uuid',
                                             username='user',
                                             password='pass')

    @asynctest.patch('juju.client.connector.Connector.connect')
    async def test_with_endpoint_and_uuid_with_bakery(self, mock_connect, _):
        m = Model()
        await m.connect(endpoint='0.1.2.3:4566',
                        uuid='some-uuid',
                        bakery_client='bakery')
        mock_connect.assert_called_once_with(endpoint='0.1.2.3:4566',
                                             uuid='some-uuid',
                                             bakery_client='bakery')

    @asynctest.patch('juju.client.connector.Connector.connect')
    async def test_with_endpoint_and_uuid_with_macaroon(self, mock_connect, _):
        m = Model()
        with self.assertRaises(TypeError):
            await m.connect(endpoint='0.1.2.3:4566',
                            uuid='some-uuid',
                            username='user')
        await m.connect(endpoint='0.1.2.3:4566',
                        uuid='some-uuid',
                        macaroons=['macaroon'])
        mock_connect.assert_called_with(endpoint='0.1.2.3:4566',
                                        uuid='some-uuid',
                                        macaroons=['macaroon'])
        await m.connect(endpoint='0.1.2.3:4566',
                        uuid='some-uuid',
                        bakery_client='bakery',
                        macaroons=['macaroon'])
        mock_connect.assert_called_with(endpoint='0.1.2.3:4566',
                                        uuid='some-uuid',
                                        bakery_client='bakery',
                                        macaroons=['macaroon'])

    @asynctest.patch('juju.client.connector.Connector.connect_model')
    @asynctest.patch('juju.client.connector.Connector.connect')
    async def test_with_posargs(self, mock_connect, mock_connect_model, _):
        m = Model()
        await m.connect('foo')
        mock_connect_model.assert_called_once_with('foo')
        with self.assertRaises(TypeError):
            await m.connect('endpoint', 'uuid')
        with self.assertRaises(TypeError):
            await m.connect('endpoint', 'uuid', 'user')
        await m.connect('endpoint', 'uuid', 'user', 'pass')
        mock_connect.assert_called_once_with(endpoint='endpoint',
                                             uuid='uuid',
                                             username='user',
                                             password='pass')
        await m.connect('endpoint', 'uuid', 'user', 'pass', 'cacert', 'bakery',
                        'macaroons', 'loop', 'max_frame_size')
        mock_connect.assert_called_with(endpoint='endpoint',
                                        uuid='uuid',
                                        username='user',
                                        password='pass',
                                        cacert='cacert',
                                        bakery_client='bakery',
                                        macaroons='macaroons',
                                        loop='loop',
                                        max_frame_size='max_frame_size')
