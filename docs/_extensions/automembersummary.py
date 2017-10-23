# Copyright 2014-2015 Canonical Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import importlib
import inspect
import textwrap

from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.errors import SphinxError
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles


class AutoMemberSummary(Directive):
    required_arguments = 1

    def run(self):
        module_name = self.arguments[0]

        try:
            module = importlib.import_module(module_name)
        except ImportError:
            raise SphinxError("Unable to generate reference docs for %s, "
                              "could not import" % (module_name))

        divider = '+{:-<80}+'.format('')
        row = '| {:<78} |'.format
        lines = []
        for member_name, member in inspect.getmembers(module):
            if not self._filter(module_name, member_name, member):
                continue
            summary = textwrap.wrap(self._get_summary(member), 78) or ['']
            link = '`{} <#{}>`_'.format(member_name,
                                        '.'.join([module_name,
                                                  member_name]))
            methods = ['* `{} <#{}>`_'.format(n,
                                              '.'.join([module_name,
                                                        member_name,
                                                        n]))
                       for n, m in inspect.getmembers(member)
                       if not n.startswith('_') and inspect.isfunction(m)]

            lines.append(divider)
            lines.append(row(link))
            lines.append(divider)
            for line in summary:
                lines.append(row(line))
            if methods:
                lines.append(row(''))
                lines.append(row('Methods:'))
                lines.append(row(''))
                for i, method in enumerate(methods):
                    lines.append(row(method))
        lines.append(divider)
        content = '\n'.join(lines)

        result = self._parse(content, '<automembersummary>')
        return result

    def _get_summary(self, member):
        doc = (member.__doc__ or '').splitlines()

        # strip any leading blank lines
        while doc and not doc[0].strip():
            doc.pop(0)

        # strip anything after the first blank line
        for i, piece in enumerate(doc):
            if not piece.strip():
                doc = doc[:i]
                break

        return " ".join(doc).strip()

    def _filter(self, module_name, member_name, member):
        if member_name.startswith('_'):
            return False
        if hasattr(member, '__module__'):
            # skip imported classes & functions
            return member.__module__.startswith(module_name)
        elif hasattr(member, '__name__'):
            # skip imported modules
            return member.__name__.startswith(module_name)
        else:
            return False  # skip instances
        return True

    def _parse(self, rst_text, annotation):
        result = ViewList()
        for line in rst_text.split("\n"):
            result.append(line, annotation)
        node = nodes.paragraph()
        node.document = self.state.document
        nested_parse_with_titles(self.state, result, node)
        return node.children


def setup(app):
    app.add_directive('automembersummary', AutoMemberSummary)
