# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from . import model


class Action(model.ModelEntity):

    def __init__(self, entity_id, model, history_index=-1, connected=True):
        super().__init__(entity_id, model, history_index, connected)
        self.results = {}
        self._status = self.data['status']

    @property
    def status(self):
        return self._status

    async def fetch_output(self):
        completed_action = await self.model._get_completed_action(self.id)
        self.results = completed_action.output or {}
        self._status = completed_action.status

    async def wait(self):
        self.results or await self.fetch_output()
        return self
