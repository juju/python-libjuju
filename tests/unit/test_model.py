# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import unittest
from unittest.mock import patch, PropertyMock

import mock

import pytest
import datetime

from juju.client.jujudata import FileJujuData
from juju.model import Model
from juju.application import Application
from juju import jasyncio
from juju.errors import JujuConnectionError, JujuError


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


class TestContextManager(unittest.IsolatedAsyncioTestCase):
    @mock.patch('juju.model.Model.disconnect')
    @mock.patch('juju.model.Model.connect')
    async def test_normal_use(self, mock_connect, mock_disconnect):

        async with Model() as model:
            self.assertTrue(isinstance(model, Model))

        self.assertTrue(mock_connect.called)
        self.assertTrue(mock_disconnect.called)

    @mock.patch('juju.model.Model.disconnect')
    @mock.patch('juju.model.Model.connect')
    async def test_exception(self, mock_connect, mock_disconnect):

        class SomeException(Exception):
            pass

        with self.assertRaises(SomeException):
            async with Model():
                raise SomeException()

        self.assertTrue(mock_connect.called)
        self.assertTrue(mock_disconnect.called)

    async def test_no_current_connection(self):

        class NoControllerJujuData(FileJujuData):
            def current_controller(self):
                return ""

        with self.assertRaises(JujuConnectionError):
            async with Model(jujudata=NoControllerJujuData()):
                pass


@mock.patch('juju.model.Model._after_connect')
class TestModelConnect(unittest.IsolatedAsyncioTestCase):
    @mock.patch('juju.client.connector.Connector.connect_model')
    async def test_no_args(self, mock_connect_model, _):
        m = Model()
        mock_connect_model.side_effect = [("_", "uuid")]
        await m.connect()
        mock_connect_model.assert_called_once_with(None)

    @mock.patch('juju.client.connector.Connector.connect_model')
    async def test_with_model_name(self, mock_connect_model, _):
        m = Model()
        mock_connect_model.side_effect = [("_", "uuid")]
        await m.connect(model_name='foo')
        mock_connect_model.assert_called_once_with('foo')

    @mock.patch('juju.client.connector.Connector.connect_model')
    async def test_with_endpoint_but_no_uuid(self, mock_connect_model, _):
        m = Model()
        mock_connect_model.side_effect = [("_", "uuid")]
        with self.assertRaises(TypeError):
            await m.connect(endpoint='0.1.2.3:4566')
        self.assertEqual(mock_connect_model.call_count, 0)

    @mock.patch('juju.client.connector.Connector.connect')
    async def test_with_endpoint_and_uuid_no_auth(self, mock_connect, _):
        m = Model()
        with self.assertRaises(TypeError):
            await m.connect(endpoint='0.1.2.3:4566', uuid='some-uuid')
        self.assertEqual(mock_connect.call_count, 0)

    @mock.patch('juju.client.connector.Connector.connect')
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

    @mock.patch('juju.client.connector.Connector.connect')
    async def test_with_endpoint_and_uuid_with_bakery(self, mock_connect, _):
        m = Model()
        await m.connect(endpoint='0.1.2.3:4566',
                        uuid='some-uuid',
                        bakery_client='bakery')
        mock_connect.assert_called_once_with(endpoint='0.1.2.3:4566',
                                             uuid='some-uuid',
                                             bakery_client='bakery')

    @mock.patch('juju.client.connector.Connector.connect')
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

    @mock.patch('juju.client.connector.Connector.connect_model')
    @mock.patch('juju.client.connector.Connector.connect')
    async def test_with_posargs(self, mock_connect, mock_connect_model, _):
        m = Model()
        mock_connect_model.side_effect = [("_", "uuid")]
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
                        'macaroons', 'max_frame_size')
        mock_connect.assert_called_with(endpoint='endpoint',
                                        uuid='uuid',
                                        username='user',
                                        password='pass',
                                        cacert='cacert',
                                        bakery_client='bakery',
                                        macaroons='macaroons',
                                        max_frame_size='max_frame_size')


# Patch timedelta to immediately force a timeout to avoid introducing an unnecessary delay in the test failing.
# It should be safe to always set it up to lead to a timeout.
@patch('juju.model.timedelta', new=lambda *a, **kw: datetime.timedelta(0))
class TestModelWaitForIdle(unittest.IsolatedAsyncioTestCase):
    async def test_no_args(self):
        m = Model()
        with self.assertWarns(DeprecationWarning):
            # no apps so should return right away
            await m.wait_for_idle(wait_for_active=True)

    async def test_apps_no_lst(self):
        m = Model()
        with self.assertRaises(JujuError):
            # apps arg has to be a List[str]
            await m.wait_for_idle(apps="should-be-list")

        with self.assertRaises(JujuError):
            # apps arg has to be a List[str]
            await m.wait_for_idle(apps=3)

        with self.assertRaises(JujuError):
            # apps arg has to be a List[str]
            await m.wait_for_idle(apps=[3])

    async def test_timeout(self):
        m = Model()
        with self.assertRaises(jasyncio.TimeoutError) as cm:
            # no apps so should timeout after timeout period
            await m.wait_for_idle(apps=["nonexisting_app"])
        self.assertEqual(str(cm.exception), "Timed out waiting for model:\nnonexisting_app (missing)")

    @pytest.mark.wait_for_idle
    async def test_wait_for_active_status(self):
        app_status = 'active'
        # create a custom apps mock
        from types import SimpleNamespace
        app = SimpleNamespace(
            status=app_status,
            units=[SimpleNamespace(
                name="mockunit/0",
                workload_status='active',
                workload_status_message="workload_status_message",
                machine=None,
                agent_status="idle",
            )],
        )

        app.get_status = mock.AsyncMock(return_value=app_status)
        apps = {"dummy_app": app}

        with patch.object(Model, 'applications', new_callable=PropertyMock) as mock_apps:
            mock_apps.return_value = apps
            m = Model()

            # pass "active" via `status` (str)
            await m.wait_for_idle(apps=["dummy_app"], status="active")

            # pass "active" via `wait_for_active` (bool; deprecated)
            await m.wait_for_idle(apps=["dummy_app"], wait_for_active=True)

            # use both `status` and `wait_for_active` - `wait_for_active` takes precedence
            await m.wait_for_idle(apps=["dummy_app"], wait_for_active=True, status="doesn't matter")

        mock_apps.assert_called_with()

    @pytest.mark.wait_for_idle
    async def test_wait_for_active_units_waiting_application(self):
        # If the app is in waiting state, then wait more even if the units are ready
        app_status = 'waiting'
        # create a custom apps mock
        from types import SimpleNamespace
        app = SimpleNamespace(
            status=app_status,
            units=[SimpleNamespace(
                name="mockunit/0",
                workload_status='active',
                workload_status_message="workload_status_message",
                machine=None,
                agent_status="idle",
            ),
                SimpleNamespace(
                    name="mockunit/1",
                    workload_status='active',
                    workload_status_message="workload_status_message",
                    machine=None,
                    agent_status="idle",
            )],
        )

        app.get_status = mock.AsyncMock(return_value=app_status)
        apps = {"dummy_app": app}

        with patch.object(Model, 'applications', new_callable=PropertyMock) as mock_apps:
            mock_apps.return_value = apps
            m = Model()

            with self.assertRaises(jasyncio.TimeoutError):
                await m.wait_for_idle(apps=["dummy_app"], status="active")

        mock_apps.assert_called_with()

    @pytest.mark.wait_for_idle
    async def test_wait_for_active_units_waiting_for_units(self):
        # If user wants to see a particular number of units, then application may be in a waiting
        # state, return when there's at least that number of units in the desired state
        app_status = 'waiting'
        # create a custom apps mock
        from types import SimpleNamespace
        app = SimpleNamespace(
            status=app_status,
            units=[SimpleNamespace(
                name="mockunit/0",
                workload_status='active',
                workload_status_message="workload_status_message",
                machine=None,
                agent_status="idle",
            ),
                SimpleNamespace(
                    name="mockunit/1",
                    workload_status='waiting',
                    workload_status_message="workload_status_message",
                    machine=None,
                    agent_status="idle",
            )],
        )

        app.get_status = mock.AsyncMock(return_value=app_status)
        apps = {"dummy_app": app}

        with patch.object(Model, 'applications', new_callable=PropertyMock) as mock_apps:
            mock_apps.return_value = apps
            m = Model()

            await m.wait_for_idle(apps=["dummy_app"], status="active", wait_for_at_least_units=1,
                                  timeout=None)

        mock_apps.assert_called_with()
