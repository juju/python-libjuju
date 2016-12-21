from collections import namedtuple

from .facade import Type

__all__ = [
    'Delta',
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
