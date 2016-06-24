from .client import client


def get_entity_delta(d):
    _delta_types = {
        'application': ApplicationDelta,
        'machine': MachineDelta,
        'unit': UnitDelta,
        'action': ActionDelta,
    }

    return _delta_types[d.entity](d.deltas)


class EntityDelta(client.Delta):
    def get_id(self):
        return self.data['Id']

    def get_entity_class(self):
        return None


class ApplicationDelta(EntityDelta):
    def get_id(self):
        return self.data['Name']

    def get_entity_class(self):
        from .application import Application
        return Application


class MachineDelta(EntityDelta):
    def get_entity_class(self):
        from .machine import Machine
        return Machine


class UnitDelta(EntityDelta):
    def get_id(self):
        return self.data['Name']

    def get_entity_class(self):
        from .unit import Unit
        return Unit


class ActionDelta(EntityDelta):
    def get_entity_class(self):
        from .action import Action
        return Action
