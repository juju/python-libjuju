from io import StringIO
from textwrap import indent


class CodeWriter(StringIO):
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
