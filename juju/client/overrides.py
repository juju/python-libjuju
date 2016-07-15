from collections import namedtuple

from .facade import Type

__all__ = [
    'Delta',
]


class Delta(Type):
    _toSchema = {'deltas': 'deltas'}
    _toPy = {'deltas': 'deltas'}

    def __init__(self, deltas=None):
        '''
        deltas : [str, str, object]
        '''
        self.deltas = deltas

        Change = namedtuple('Change', 'entity type data')
        change = Change(*self.deltas)

        self.entity = change.entity
        self.type = change.type
        self.data = change.data

    @classmethod
    def from_json(cls, data):
        return cls(deltas=data)
