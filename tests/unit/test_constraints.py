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
        self.assertEqual(_("foo,bar"), "foo,bar")

    def test_normalize_list_val(self):
        _ = constraints.normalize_list_value

        self.assertEqual(_("foo"), ["foo"])
        self.assertEqual(_("foo,bar"), ["foo", "bar"])

    def test_parse_constraints(self):
        _ = constraints.parse

        self.assertEqual(
            _("mem=10G"),
            {"mem": 10 * 1024}
        )

        self.assertEqual(
            _("mem=10G foo=bar,baz tags=tag1 spaces=space1,space2"),
            {"mem": 10 * 1024,
             "foo": "bar,baz",
             "tags": ["tag1"],
             "spaces": ["space1", "space2"]}
        )

    def test_parse_storage_constraint(self):
        _ = constraints.parse_storage_constraint

        self.assertEqual(
            _("pool,1M"),
            {"pool": "pool",
             "count": 1,
             "size": 1 * 1024 ** 0}
        )
        self.assertEqual(
            _("pool,"),
            {"pool": "pool",
             "count": 1}
        )
        self.assertEqual(
            _("1M"),
            {"size": 1 * 1024 ** 0,
             "count": 1}
        )
        self.assertEqual(
            _("p,1G"),
            {"pool": "p",
             "count": 1,
             "size": 1 * 1024 ** 1}
        )
        self.assertEqual(
            _("p,0.5T"),
            {"pool": "p",
             "count": 1,
             "size": 512 * 1024 ** 1}
        )
        self.assertEqual(
            _("3,0.5T"),
            {"count": 3,
             "size": 512 * 1024 ** 1}
        )
        self.assertEqual(
            _("0.5T,3"),
            {"count": 3,
             "size": 512 * 1024 ** 1}
        )

    def test_parse_device_constraint(self):
        _ = constraints.parse_device_constraint

        self.assertEqual(
            _("nvidia.com/gpu"),
            {"type": "nvidia.com/gpu",
             "count": 1}
        )
        self.assertEqual(
            _("2,nvidia.com/gpu"),
            {"type": "nvidia.com/gpu",
             "count": 2}
        )
        self.assertEqual(
            _("3,nvidia.com/gpu,gpu=nvidia-tesla-p100"),
            {"type": "nvidia.com/gpu",
             "count": 3,
             "attributes": {
                 "gpu": "nvidia-tesla-p100"
             }}
        )
        self.assertEqual(
            _("3,nvidia.com/gpu,gpu=nvidia-tesla-p100;2ndattr=another-attr"),
            {"type": "nvidia.com/gpu",
             "count": 3,
             "attributes": {
                 "gpu": "nvidia-tesla-p100",
                 "2ndattr": "another-attr"
             }}
        )
