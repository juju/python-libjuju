'''Replace auto-generated classes with our own, where necessary.
'''
import sys

from . import _client, _definitions, overrides  # isort:skip
from .old_clients import _client as _2_9_client
from .old_clients import _definitions as _2_9_definitions

for o in overrides.__all__:
    if "Facade" not in o:
        # Override stuff in _definitions, which is all imported
        # into _client. We Monkey patch both the original class and
        # the ref in _client (import shenanigans are fun!)
        setattr(_definitions, o, getattr(overrides, o))
        setattr(_client, o, getattr(overrides, o))
        setattr(_2_9_definitions, o, getattr(overrides, o))
        setattr(_2_9_client, o, getattr(overrides, o))
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
    # This unfortunately needs to be a separate loop
    for old_client_version in _2_9_client.CLIENTS.values():
        try:
            c_type = getattr(old_client_version, o)
        except AttributeError:
            # Not all the _client<version> modules may have the
            # facade. That's okay -- we just skip over them.
            continue
        o_type = getattr(overrides, o)
        for a in dir(o_type):
            if not a.startswith('_'):
                setattr(c_type, a, getattr(o_type, a))

from ._client import *  # noqa, isort:skip


class ClientModuleClass:
    def __init__(self):
        """
        new_client (bool): True if we're working with juju>3.0
        """
        self.new_client = None
        self.client_module = _client

    __all__ = list(set(vars().keys()) - {'__module__', '__qualname__'})

    def __getattr__(self, item):
        return getattr(self.client_module, item)

    def set_new_client(self, server_version):
        self.new_client = server_version.startswith('3.')
        if not self.new_client:
            self.client_module = _2_9_client


"""
This is basically a hack to turn this module into a dynamic
binding registry, by replacing this module object with a class
instance that acts like a module in sys.modules in the runtime.

Based on the value of the 'new_client' variable
(True if >3.0, False if 2.9) we dynamically change the modules
from which we get the actual bindings behind the scenes.
Theoretically the new_client should only be set once, but we
have to keep it dynamic since there's no way for libjuju to
know when and with which juju version a connection will be
established.

Bindings for >3.0 are coming from _client & _definitions
Bindings for 2.9 are coming from _2_9_client & _2_9_client
"""
sys.modules[__name__] = ClientModuleClass()
