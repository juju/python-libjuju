import unittest

import mock


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

        loop = mock.MagicMock()
        model = Model(loop=loop)
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
