from . import model


class Action(model.ModelEntity):

    def __init__(self, entity_id, model, history_index=-1, connected=True):
        super().__init__(entity_id, model, history_index, connected)
        self.results = {}

    @property
    def status(self):
        return self.data['status']

    async def wait(self):
        self.results = await self.model.get_action_output(self.id)
        return self
