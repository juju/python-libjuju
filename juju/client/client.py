'''Replace auto-generated classes with our own, where necessary.

'''

from . import _client
from . import overrides


for o in overrides.__all__:
    setattr(_client, o, getattr(overrides, o))

from ._client import *  # noqa
