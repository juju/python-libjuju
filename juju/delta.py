from .client import client


def get_entity_delta(d):
    _delta_types = {
        'action': ActionDelta,
        'application': ApplicationDelta,
        'annotation': AnnotationDelta,
        'machine': MachineDelta,
        'unit': UnitDelta,
        'relation': RelationDelta,
    }

    return _delta_types[d.entity](d.deltas)


class EntityDelta(client.Delta):
    def get_id(self):
        return self.data['id']

    def get_entity_class(self):
        return None


class ActionDelta(EntityDelta):
    def get_entity_class(self):
        from .action import Action
        return Action


class ApplicationDelta(EntityDelta):
    def get_id(self):
        return self.data['name']

    def get_entity_class(self):
        from .application import Application
        return Application


class AnnotationDelta(EntityDelta):
    def get_id(self):
        return self.data['tag']

    def get_entity_class(self):
        from .annotation import Annotation
        return Annotation


class MachineDelta(EntityDelta):
    def get_entity_class(self):
        from .machine import Machine
        return Machine


class UnitDelta(EntityDelta):
    def get_id(self):
        return self.data['name']

    def get_entity_class(self):
        from .unit import Unit
        return Unit


class RelationDelta(EntityDelta):
    def get_entity_class(self):
        from .relation import Relation
        return Relation
