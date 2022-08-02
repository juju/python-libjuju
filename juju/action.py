from . import model


class Action(model.ModelEntity):
    @property
    def status(self):
        return self.data['status']

    async def wait(self):
        return await self.model.get_action_output(self.id)
