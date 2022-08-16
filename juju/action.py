from . import model


class Action(model.ModelEntity):

    def __init__(self, entity_id, model, history_index=-1, connected=True):
        super().__init__(entity_id, model, history_index, connected)
        self.results = {}

    @property
    def status(self):
        return self.data['status']

    async def fetch_output(self):
        self.results = await self.model.get_action_output(self.id)

    async def wait(self):
        self.results or await self.fetch_output()
        return self
