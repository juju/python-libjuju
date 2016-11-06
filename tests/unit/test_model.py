import unittest


class TestObserver(unittest.TestCase):
    def _make_observer(self, *args):
        from juju.model import _Observer
        return _Observer(*args)

    def _make_delta(self, entity, type_, data=None):
        from juju.delta import ApplicationDelta
        return ApplicationDelta([entity, type_, data])

    def test_cares_about_id(self):
        id_ = 'foo'

        o = self._make_observer(
            None, None, None, id_, None)

        delta = self._make_delta(
            'application', 'change', dict(name=id_))

        self.assertTrue(o.cares_about(delta))

    def test_cares_about_type(self):
        type_ = 'application'

        o = self._make_observer(
            None, type_, None, None, None)

        delta = self._make_delta(
            type_, 'change', dict(name='foo'))

        self.assertTrue(o.cares_about(delta))

    def test_cares_about_action(self):
        action = 'change'

        o = self._make_observer(
            None, None, action, None, None)

        delta = self._make_delta(
            'application', action, dict(name='foo'))

        self.assertTrue(o.cares_about(delta))

    def test_cares_about_predicate(self):
        def predicate(delta):
            return delta.data.get('fizz') == 'bang'

        o = self._make_observer(
            None, None, None, None, predicate)

        delta = self._make_delta(
            'application', 'change', dict(fizz='bang'))

        self.assertTrue(o.cares_about(delta))
