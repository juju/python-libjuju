from collections import namedtuple

from .facade import ReturnMapping, Type, TypeEncoder
from .import _client


__all__ = [
    'Delta',
]

__patches__ = [
    'ResourcesFacade',
    'AllWatcherFacade'
]


class Delta(Type):
    """A single websocket delta.

    :ivar entity: The entity name, e.g. 'unit', 'application'
    :vartype entity: str

    :ivar type: The delta type, e.g. 'add', 'change', 'remove'
    :vartype type: str

    :ivar data: The raw delta data
    :vartype data: dict

    NOTE: The 'data' variable above is being incorrectly cross-linked by a
    Sphinx bug: https://github.com/sphinx-doc/sphinx/issues/2549

    """
    _toSchema = {'deltas': 'deltas'}
    _toPy = {'deltas': 'deltas'}

    def __init__(self, deltas=None):
        """
        :param deltas: [str, str, object]

        """
        self.deltas = deltas

        Change = namedtuple('Change', 'entity type data')
        change = Change(*self.deltas)

        self.entity = change.entity
        self.type = change.type
        self.data = change.data

    @classmethod
    def from_json(cls, data):
        return cls(deltas=data)


class ResourcesFacade(Type):
    """Patch parts of ResourcesFacade to make it work.
    """

    @ReturnMapping(_client.AddPendingResourcesResult)
    async def AddPendingResources(self, application_tag, charm_url, resources):
        """Fix the calling signature of AddPendingResources.

        The ResourcesFacade doesn't conform to the standard facade pattern in
        the Juju source, which leads to the schemagened code not matching up
        properly with the actual calling convention in the API.  There is work
        planned to fix this in Juju, but we have to work around it for now.

        application_tag : str
        charm_url : str
        resources : typing.Sequence<+T_co>[~CharmResource]<~CharmResource>
        Returns -> typing.Union[_ForwardRef('ErrorResult'),
                                typing.Sequence<+T_co>[str]]
        """
        # map input types to rpc msg
        _params = dict()
        msg = dict(type='Resources',
                   request='AddPendingResources',
                   version=1,
                   params=_params)
        _params['tag'] = application_tag
        _params['url'] = charm_url
        _params['resources'] = resources
        reply = await self.rpc(msg)
        return reply

class AllWatcherFacade(Type):
    """
    Patch rpc method of allwatcher to add in 'id' stuff.

    """
    async def rpc(self, msg):
        if not hasattr(self, 'Id'):
            client = _client.ClientFacade.from_connection(self.connection)

            result = await client.WatchAll()
            self.Id = result.watcher_id

        msg['Id'] = self.Id
        result =  await self.connection.rpc(msg, encoder=TypeEncoder)
        return result
