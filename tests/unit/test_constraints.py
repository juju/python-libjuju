#
# Test our constraints parser
#

import unittest

from juju import constraints

class TestConstraints(unittest.TestCase):

    def test_mem_regex(self):
        m = constraints.MEM
        self.assertTrue(m.match("10G"))
        self.assertTrue(m.match("1G"))
        self.assertFalse(m.match("1Gb"))
        self.assertFalse(m.match("a1G"))
        self.assertFalse(m.match("1000"))

    def test_normalize_key(self):
        _ = constraints.normalize_key

        self.assertEqual(_("test-key"), "test_key")
        self.assertEqual(_("test-key  "), "test_key")
        self.assertEqual(_("  test-key"), "test_key")
        self.assertEqual(_("TestKey"), "test_key")
        self.assertEqual(_("testKey"), "test_key")

    def test_normalize_val(self):
        _ = constraints.normalize_value

        self.assertEqual(_("10G"), 10 * 1024)
        self.assertEqual(_("10M"), 10)
        self.assertEqual(_("10"), 10)
        self.assertEqual(_("foo,bar"), ["foo", "bar"])

    def test_parse_constraints(self):
        _ = constraints.parse

        self.assertEqual(
            _("mem=10G"),
            {"mem": 10 * 1024}
        )

        self.assertEqual(
            _("mem=10G foo=bar,baz"),
            {"mem": 10 * 1024, "foo": ["bar", "baz"]}
        )
