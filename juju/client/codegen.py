from collections import defaultdict
from io import StringIO
from textwrap import indent


class CodeWriter(StringIO):
    """
    Blob of text that, when used in the context of facade.py, ends up
    holding the source code for a Python class and associated methods.

    """
    INDENT = "    "

    CLASS = 0
    METHOD = 1

    def write(self, msg, depth=0):
        if depth:
            prefix = self.INDENT * depth
            msg = indent(msg, prefix)

        return super(CodeWriter, self).write(msg)

    def __str__(self):
        return super(CodeWriter, self).getvalue()


class Capture(defaultdict):
    """
    A collection of CodeWriter objects, together representing a Python
    module.

    """

    def __init__(self, default_factory=CodeWriter, *args, **kwargs):
        super(Capture, self).__init__(default_factory, *args, **kwargs)

    def clear(self, name):
        """
        Reset one of the keys in this class, if it exists.

        This is necessary, because we don't worry about de-duplicating
        the schemas for each version of juju up front, and this gives
        us a way to sort of de-duplicate on the fly, by resetting a
        specific CodeWriter instance before we start to write a class
        into it.

        """
        try:
            del self[name]
        except KeyError:
            pass
