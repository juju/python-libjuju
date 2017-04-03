'''Replace auto-generated classes with our own, where necessary.

'''

from . import _client
from . import overrides


for o in overrides.__all__:
    setattr(_client, o, getattr(overrides, o))

for o in overrides.__patches__:
    c_type = getattr(_client, o)
    o_type = getattr(overrides, o)
    for a in dir(o_type):
        if not a.startswith('_'):
            setattr(c_type, a, getattr(o_type, a))

from ._client import *  # noqa
