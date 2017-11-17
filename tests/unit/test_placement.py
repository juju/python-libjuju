#
# Test our placement helper
#

import unittest

from juju import placement


class TestPlacement(unittest.TestCase):

    def test_parse_both_specified(self):
        res = placement.parse("foo:bar")
        self.assertEqual(res[0].scope, "foo")
        self.assertEqual(res[0].directive, "bar")

    def test_parse_machine(self):
        res = placement.parse("22")
        self.assertEqual(res[0].scope, "#")
        self.assertEqual(res[0].directive, "22")
