#
# Test our placement helper
#

import unittest

from juju import placement
from juju.client import client

class TestPlacement(unittest.TestCase):

    def test_parse_both_specified(self):
        res = placement.parse("foo:bar")
        self.assertEqual(res.scope, "foo")
        self.assertEqual(res.directive, "bar")

    def test_parse_machine(self):
        res = placement.parse("22")
        self.assertEqual(res.scope, "#")
        self.assertEqual(res.directive, "22")
