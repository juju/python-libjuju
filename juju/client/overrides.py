import re
from collections import namedtuple

from . import _client, _definitions
from .facade import ReturnMapping, Type, TypeEncoder

__all__ = [
    'Delta',
    'Number',
    'Binary',
    'ConfigValue',
    'Resource',
]

__patches__ = [
    'ResourcesFacade',
    'AllWatcherFacade',
    'ActionFacade',
    'ModelSummaryWatcherFacade',
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
    async def AddPendingResources(self, application_tag="", charm_url="", resources=None):
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
        result = await self.connection.rpc(msg, encoder=TypeEncoder)
        return result


class ModelSummaryWatcherFacade(Type):
    """
    Patch rpc method of model summary watcher to add in 'id' stuff.

    """
    async def rpc(self, msg):
        if not hasattr(self, 'Id'):
            raise RuntimeError('Missing "Id" field')

        msg['Id'] = self.Id
        result = await self.connection.rpc(msg, encoder=TypeEncoder)
        return result


class ActionFacade(Type):

    class _FindTagsResults(Type):
        _toSchema = {'matches': 'matches'}
        _toPy = {'matches': 'matches'}

        def __init__(self, matches=None, **unknown_fields):
            '''
            FindTagsResults wraps the mapping between the requested prefix and the
            matching tags for each requested prefix.

            Matches map[string][]Entity `json:"matches"`
            '''
            self.matches = {}
            matches = matches or {}
            for prefix, tags in matches.items():
                self.matches[prefix] = [_definitions.Entity.from_json(r)
                                        for r in tags]

    @ReturnMapping(_FindTagsResults)
    async def FindActionTagsByPrefix(self, prefixes):
        '''
        prefixes : typing.Sequence[str]
        Returns -> typing.Sequence[~Entity]
        '''
        # map input types to rpc msg
        _params = dict()
        msg = dict(type='Action',
                   request='FindActionTagsByPrefix',
                   version=2,
                   params=_params)
        _params['prefixes'] = prefixes
        reply = await self.rpc(msg)
        return reply


class Number(_definitions.Number):
    """
    This type represents a semver string.

    Because it is not standard JSON, the typical from_json parsing fails and
    the parsing must be handled specially.

    See https://github.com/juju/version for more info.
    """
    numberPat = re.compile(r'^(\d{1,9})\.(\d{1,9})(?:\.|-([a-z]+))(\d{1,9})(\.\d{1,9})?$')  # noqa

    def __init__(self, major=None, minor=None, patch=None, tag=None,
                 build=None, **unknown_fields):
        '''
        major : int
        minor : int
        patch : int
        tag : str
        build : int
        '''
        self.major = int(major or '0')
        self.minor = int(minor or '0')
        self.patch = int(patch or '0')
        self.tag = tag or ''
        self.build = int(build or '0')

    def __repr__(self):
        return '<Number major={} minor={} patch={} tag={} build={}>'.format(
            self.major, self.minor, self.patch, self.tag, self.build)

    def __str__(self):
        return self.serialize()

    @property
    def _cmp(self):
        return (self.major, self.minor, self.tag, self.patch, self.build)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self._cmp == other._cmp

    def __lt__(self, other):
        return self._cmp < other._cmp

    def __le__(self, other):
        return self._cmp <= other._cmp

    def __gt__(self, other):
        return self._cmp > other._cmp

    def __ge__(self, other):
        return self._cmp >= other._cmp

    @classmethod
    def from_json(cls, data):
        parsed = None
        if isinstance(data, cls):
            return data
        elif data is None:
            return cls()
        elif isinstance(data, dict):
            parsed = data
        elif isinstance(data, str):
            match = cls.numberPat.match(data)
            if match:
                parsed = {
                    'major': match.group(1),
                    'minor': match.group(2),
                    'tag': match.group(3),
                    'patch': match.group(4),
                    'build': (match.group(5)[1:] if match.group(5)
                              else 0),
                }
        if not parsed:
            raise TypeError('Unable to parse Number version string: '
                            '{}'.format(data))
        d = {}
        for k, v in parsed.items():
            d[cls._toPy.get(k, k)] = v

        return cls(**d)

    def serialize(self):
        s = ""
        if not self.tag:
            s = "{}.{}.{}".format(self.major, self.minor, self.patch)
        else:
            s = "{}.{}-{}{}".format(self.major, self.minor, self.tag,
                                    self.patch)
        if self.build:
            s = "{}.{}".format(s, self.build)
        return s

    def to_json(self):
        return self.serialize()


class Binary(_definitions.Binary):
    """
    This type represents a semver string with additional series and arch info.

    Because it is not standard JSON, the typical from_json parsing fails and
    the parsing must be handled specially.

    See https://github.com/juju/version for more info.
    """
    binaryPat = re.compile(r'^(\d{1,9})\.(\d{1,9})(?:\.|-([a-z]+))(\d{1,9})(\.\d{1,9})?-([^-]+)-([^-]+)$')  # noqa

    def __init__(self, number=None, series=None, arch=None, **unknown_fields):
        '''
        number : Number
        series : str
        arch : str
        '''
        self.number = Number.from_json(number)
        self.series = series
        self.arch = arch

    def __repr__(self):
        return '<Binary number={} series={} arch={}>'.format(
            self.number, self.series, self.arch)

    def __str__(self):
        return self.serialize()

    def __eq__(self, other):
        return (
            isinstance(other, type(self)) and
            other.number == self.number and
            other.series == self.series and
            other.arch == self.arch)

    @classmethod
    def from_json(cls, data):
        parsed = None
        if isinstance(data, cls):
            return data
        elif data is None:
            return cls()
        elif isinstance(data, dict):
            parsed = data
        elif isinstance(data, str):
            match = cls.binaryPat.match(data)
            if match:
                parsed = {
                    'number': {
                        'major': match.group(1),
                        'minor': match.group(2),
                        'tag': match.group(3),
                        'patch': match.group(4),
                        'build': (match.group(5)[1:] if match.group(5)
                                  else 0),
                    },
                    'series': match.group(6),
                    'arch': match.group(7),
                }
        if parsed is None:
            raise TypeError('Unable to parse Binary version string: '
                            '{}'.format(data))
        d = {}
        for k, v in parsed.items():
            d[cls._toPy.get(k, k)] = v

        return cls(**d)

    def serialize(self):
        return "{}-{}-{}".format(self.number.serialize(),
                                 self.series, self.arch)

    def to_json(self):
        return self.serialize()


class ConfigValue(_definitions.ConfigValue):
    def __repr__(self):
        return '<{} source={} value={}>'.format(type(self).__name__,
                                                repr(self.source),
                                                repr(self.value))


class Resource(Type):
    _toSchema = {'application': 'application',
                 'charmresource': 'CharmResource',
                 'id_': 'id',
                 'pending_id': 'pending-id',
                 'timestamp': 'timestamp',
                 'username': 'username',
                 'name': 'name',
                 'origin': 'origin'}
    _toPy = {'CharmResource': 'charmresource',
             'application': 'application',
             'id': 'id_',
             'pending-id': 'pending_id',
             'timestamp': 'timestamp',
             'username': 'username',
             'name': 'name',
             'origin': 'origin'}

    def __init__(self, charmresource=None, application=None, id_=None,
                 pending_id=None, timestamp=None, username=None, name=None,
                 origin=None, **unknown_fields):
        '''
        charmresource : CharmResource
        application : str
        id_ : str
        pending_id : str
        timestamp : str
        username : str
        name: str
        origin : str
        '''
        if charmresource:
            self.charmresource = _client.CharmResource.from_json(charmresource)
        else:
            self.charmresource = None
        self.application = application
        self.id_ = id_
        self.pending_id = pending_id
        self.timestamp = timestamp
        self.username = username
        self.name = name
        self.origin = origin
        self.unknown_fields = unknown_fields


class Macaroon(Type):
    _toSchema = {'signature': 'signature',
                 'caveats': 'caveats',
                 'location': 'location',
                 'identifier': 'identifier'}
    _toPy = {'signature': 'signature',
             'caveats': 'caveats',
             'location': 'location',
             'identifier': 'identifier'}

    def __init__(self, signature="", caveats=None, location=None, identifier="", **unknown_fields):
        '''
        signature : str
        caveats : typing.Sequence<+T_co>[~RemoteSpace]<~RemoteSpace>
        location : str
        identifier : str
        '''
        self.signature = signature
        self.caveats = caveats
        self.location = location
        self.identifier = identifier
        self.unknown_fields = unknown_fields


class Caveat(Type):
    _toSchema = {'cid': 'cid'}
    _toPy = {'cid': 'cid'}

    def __init__(self, cid="", **unknown_fields):
        '''
        cid : str
        '''
        self.cid = cid
        self.unknown_fields = unknown_fields
