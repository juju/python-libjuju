# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
from __future__ import annotations

from . import model
from .client import client, overrides


def get_entity_delta(d: overrides.Delta):
    return _delta_types[d.entity](d.deltas)


def get_entity_class(entity_type):
    return _delta_types[entity_type].get_entity_class()


class EntityDelta(client.Delta):
    data: dict[str, str]

    def get_id(self) -> str:
        return self.data["id"]

    @classmethod
    def get_entity_class(cls) -> type[model.ModelEntity]:
        raise NotImplementedError()


class ActionDelta(EntityDelta):
    @classmethod
    def get_entity_class(cls):
        from .action import Action

        return Action


class ApplicationDelta(EntityDelta):
    def get_id(self):
        return self.data["name"]

    @classmethod
    def get_entity_class(cls):
        from .application import Application

        return Application


class AnnotationDelta(EntityDelta):
    def get_id(self):
        return self.data["tag"]

    @classmethod
    def get_entity_class(cls):
        from .annotation import Annotation

        return Annotation


class ModelDelta(EntityDelta):
    def get_id(self):
        return self.data["model-uuid"]

    @classmethod
    def get_entity_class(cls):
        from .model import ModelInfo

        return ModelInfo


class MachineDelta(EntityDelta):
    @classmethod
    def get_entity_class(cls):
        from .machine import Machine

        return Machine


class UnitDelta(EntityDelta):
    def get_id(self):
        return self.data["name"]

    @classmethod
    def get_entity_class(cls):
        from .unit import Unit

        return Unit


class RelationDelta(EntityDelta):
    @classmethod
    def get_entity_class(cls):
        from .relation import Relation

        return Relation


class RemoteApplicationDelta(EntityDelta):
    def get_id(self):
        return self.data["name"]

    @classmethod
    def get_entity_class(cls):
        from .remoteapplication import RemoteApplication

        return RemoteApplication


class CharmDelta(EntityDelta):
    def get_id(self):
        return self.data["charm-url"]

    @classmethod
    def get_entity_class(cls):
        from .charm import Charm

        return Charm


class ApplicationOfferDelta(EntityDelta):
    def get_id(self):
        return self.data["application-name"]

    @classmethod
    def get_entity_class(cls):
        from .remoteapplication import ApplicationOffer

        return ApplicationOffer


_delta_types = {
    "action": ActionDelta,
    "annotation": AnnotationDelta,
    "application": ApplicationDelta,
    "applicationOffer": ApplicationOfferDelta,
    "charm": CharmDelta,
    "machine": MachineDelta,
    "model": ModelDelta,
    "relation": RelationDelta,
    "remoteApplication": RemoteApplicationDelta,
    "unit": UnitDelta,
}
