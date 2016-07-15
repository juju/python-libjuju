from .client import AllWatcherFacade as BaseAllWatcher
from .client import ClientFacade


class AllWatcher(BaseAllWatcher):
    async def rpc(self, msg):
        if not hasattr(self, 'Id'):
            client = ClientFacade()
            client.connect(self.connection)

            result = await client.WatchAll()
            self.Id = result.watcher_id

        msg['Id'] = self.Id
        return await super(AllWatcher, self).rpc(msg)
