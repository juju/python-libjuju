from .client import client
from .errors import JujuError


class CharmHub:
    def __init__(self, model):
        self.model = model

    async def info(self, name, channel=None):
        """info displays detailed information about a CharmHub charm. The charm
        can be specified by the exact name.

        Channel is a hint for providing the metadata for a given channel.
        Without the channel hint then only the default release will have the
        metadata.

        """
        if not name:
            raise JujuError("name expected")

        if channel is None:
            channel = ""

        facade = self._facade()
        return await facade.Info(tag="application-{}".format(name), channel=channel)

    async def find(self, query, category=None, channel=None,
                   charm_type=None, platforms=None, publisher=None,
                   relation_requires=None, relation_provides=None):
        """find queries the CharmHub store for available charms or bundles.

        """
        if charm_type is not None and charm_type not in ["charm", "bundle"]:
            raise JujuError("expected either charm or bundle for charm_type")

        facade = self._facade()
        return await facade.Find(query=query, category=category, channel=channel,
                                 type_=charm_type, platforms=platforms, publisher=publisher,
                                 relation_provides=relation_provides, relation_requires=relation_requires)

    def _facade(self):
        return client.CharmHubFacade.from_connection(self.model.connection())
