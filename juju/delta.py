from .client import client


def get_entity_delta(d):
    return _delta_types[d.entity](d.deltas)


def get_entity_class(entity_type):
    return _delta_types[entity_type].get_entity_class()


class EntityDelta(client.Delta):
    def get_id(self):
        return self.data['id']

    @classmethod
    def get_entity_class(self):
        return None


class ActionDelta(EntityDelta):
    @classmethod
    def get_entity_class(self):
        from .action import Action
        return Action


class ApplicationDelta(EntityDelta):
    def get_id(self):
        return self.data['name']

    @classmethod
    def get_entity_class(self):
        from .application import Application
        return Application


class AnnotationDelta(EntityDelta):
    def get_id(self):
        return self.data['tag']

    @classmethod
    def get_entity_class(self):
        from .annotation import Annotation
        return Annotation


class ModelDelta(EntityDelta):
    @classmethod
    def get_entity_class(self):
        from .model import ModelInfo
        return ModelInfo


class MachineDelta(EntityDelta):
    @classmethod
    def get_entity_class(self):
        from .machine import Machine
        return Machine


class UnitDelta(EntityDelta):
    def get_id(self):
        return self.data['name']

    @classmethod
    def get_entity_class(self):
        from .unit import Unit
        return Unit


class RelationDelta(EntityDelta):
    @classmethod
    def get_entity_class(self):
        from .relation import Relation
        return Relation


class RemoteApplicationDelta(EntityDelta):
    def get_id(self):
        return self.data['name']

    @classmethod
    def get_entity_class(self):
        from .remoteapplication import RemoteApplication
        return RemoteApplication


class CharmDelta(EntityDelta):
    def get_id(self):
        return self.data['charm-url']

    @classmethod
    def get_entity_class(self):
        from .charm import Charm
        return Charm


class ApplicationOfferDelta(EntityDelta):
    def get_id(self):
        return self.data['application-name']

    @classmethod
    def get_entity_class(self):
        from .remoteapplication import ApplicationOffer
        return ApplicationOffer


_delta_types = {
    'action': ActionDelta,
    'annotation': AnnotationDelta,
    'application': ApplicationDelta,
    'applicationOffer': ApplicationOfferDelta,
    'charm': CharmDelta,
    'machine': MachineDelta,
    'model': ModelDelta,
    'relation': RelationDelta,
    'remoteApplication': RemoteApplicationDelta,
    'unit': UnitDelta,
}
