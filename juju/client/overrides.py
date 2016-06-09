from .facade import Type

__all__ = [
    'Delta',
]


class Delta(Type):
    _toSchema = {'deltas': 'Deltas'}
    _toPy = {'Deltas': 'deltas'}

    def __init__(self, deltas=None):
        '''
        deltas : [str, str, object]
        '''
        self.deltas = deltas

    @classmethod
    def from_json(cls, data):
        return cls(deltas=data)
