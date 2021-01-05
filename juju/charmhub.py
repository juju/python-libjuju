from .client import client
from .errors import JujuError


class CharmHub:
    def __init__(self, model):
        self.model = model

    async def info(self, name, channel=None):
        """info displays detailed information about a CharmHub charm. The charm
        can be specified by name or by path.

        """
        if not name:
            raise JujuError("name expected")

        if channel is None:
            channel = "latest"

        facade = self._facade()
        return await facade.Info(tag="application-{}".format(name), channel=channel)

    def _facade(self):
        return client.CharmHubFacade.from_connection(self.model.connection())
