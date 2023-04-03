'''Replace auto-generated classes with our own, where necessary.
'''

from . import _client, _definitions, overrides  # isort:skip

for o in overrides.__all__:
    if "Facade" not in o:
        # Override stuff in _definitions, which is all imported
        # into _client. We Monkey patch both the original class and
        # the ref in _client (import shenanigans are fun!)
        setattr(_definitions, o, getattr(overrides, o))
        setattr(_client, o, getattr(overrides, o))
    # We shouldn't be overriding Facades!
    else:
        raise ValueError(
            "Cannot override a versioned Facade class -- you must patch "
            "it instead.")

for o in overrides.__patches__:
    # Patch a versioned Facade.
    for client_version in _client.CLIENTS.values():
        try:
            c_type = getattr(client_version, o)
        except AttributeError:
            # Not all the _client<version> modules may have the
            # facade. That's okay -- we just skip over them.
            continue
        o_type = getattr(overrides, o)
        for a in dir(o_type):
            if not a.startswith('_'):
                setattr(c_type, a, getattr(o_type, a))

from ._client import *  # noqa, isort:skip
