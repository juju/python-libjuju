from .client import AllWatcher as BaseAllWatcher
from .client import Client


class AllWatcher(BaseAllWatcher):
    async def rpc(self, msg):
        if not hasattr(self, 'Id'):
            client = Client()
            client.connect(self.connection)

            result = await client.WatchAll()
            self.Id = result.allwatcherid

        msg['Id'] = self.Id
        return await super(AllWatcher, self).rpc(msg)
