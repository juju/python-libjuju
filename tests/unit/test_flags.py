import os
import unittest

from juju.client import flags


class TestFlags(unittest.TestCase):

    def test_default_flag(self):
        os.environ[flags.PYLIBJUJU_DEV_FEATURE_FLAG] = flags.DEFAULT_VALUES_FLAG
        self.assertTrue(flags.feature_enabled(flags.DEFAULT_VALUES_FLAG))

    def test_multiple_flag(self):
        os.environ[flags.PYLIBJUJU_DEV_FEATURE_FLAG] = "xxx, {},foo, bar".format(flags.DEFAULT_VALUES_FLAG)
        self.assertTrue(flags.feature_enabled(flags.DEFAULT_VALUES_FLAG))

    def test_missing_flag(self):
        os.environ[flags.PYLIBJUJU_DEV_FEATURE_FLAG] = "foo, bar"
        self.assertFalse(flags.feature_enabled(flags.DEFAULT_VALUES_FLAG))
