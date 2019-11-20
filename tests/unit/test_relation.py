import unittest

import mock

from juju.model import Model
from juju.relation import Relation


def _make_delta(entity, type_, data=None):
    from juju.client.client import Delta
    from juju.delta import get_entity_delta

    delta = Delta([entity, type_, data])
    return get_entity_delta(delta)


class TestRelation(unittest.TestCase):
    def test_relation_does_not_match(self):
        model = Model()
        model._connector = mock.MagicMock()

        delta = _make_delta('application', 'add', dict(name='foo'))
        model.state.apply_delta(delta)
        delta = _make_delta('relation', 'bar', dict(id="uuid-1234", name='foo', endpoints=[{"application-name": "foo"}]))
        model.state.apply_delta(delta)

        rel = Relation("uuid-1234", model)
        self.assertFalse(rel.matches(["endpoint"]))

    def test_relation_does_match(self):
        model = Model()
        model._connector = mock.MagicMock()

        delta = _make_delta('application', 'add', dict(name='foo'))
        model.state.apply_delta(delta)
        delta = _make_delta('relation', 'bar', dict(id="uuid-1234", name='foo', endpoints=[{"application-name": "foo"}]))
        model.state.apply_delta(delta)

        rel = Relation("uuid-1234", model)
        self.assertFalse(rel.matches(["foo"]))

    def test_relation_does_match_remote_app(self):
        model = Model()
        model._connector = mock.MagicMock()

        delta = _make_delta('remoteApplication', 'add', dict(name='foo'))
        model.state.apply_delta(delta)
        delta = _make_delta('relation', 'bar', dict(id="uuid-1234", name='foo', endpoints=[{"application-name": "foo"}]))
        model.state.apply_delta(delta)

        rel = Relation("uuid-1234", model)
        self.assertFalse(rel.matches(["foo"]))

    def test_relation_does_not_match_anything(self):
        model = Model()
        model._connector = mock.MagicMock()

        delta = _make_delta('relation', 'bar', dict(id="uuid-1234", name='foo', endpoints=[{"application-name": "foo"}]))
        model.state.apply_delta(delta)

        rel = Relation("uuid-1234", model)
        self.assertFalse(rel.matches(["xxx"]))
