'''Replace auto-generated classes with our own, where necessary.
'''

from . import _client
from . import overrides


for o in overrides.__all__:
    # Override stuff in _client_definitions, which is all imported
    # into _client.
    if not "Facade" in o:
        setattr(_client, o, getattr(overrides, o))
    # We shouldn't be overriding Facades!
    else:
        raise ValueError(
            "Cannot override a versioned Facade class -- you must patch "
            "it instead.")

for o in overrides.__patches__:
    for c in _client.CLIENTS.values():
        try:
            c_type = getattr(c, o)
        except AttributeError:
            continue
        o_type = getattr(overrides, o)
        for a in dir(o_type):
            if not a.startswith('_'):
                setattr(c_type, a, getattr(o_type, a))

from ._client import *  # noqa
