import unittest

from juju.url import Schema, URL


class TestURLV1(unittest.TestCase):
    def test_parse_local(self):
        u = URL.parse("local:mysql")
        self.assertEqual(u, URL(Schema.LOCAL, name="mysql"))


class TestURLV2(unittest.TestCase):
    def test_parse_charmhub(self):
        u = URL.parse("ch:arm64/bionic/mysql-1")
        self.assertEqual(u, URL(Schema.CHARM_HUB, name="mysql", architecture="arm64", series="bionic", revision=1))

    def test_parse_charmhub_with_no_series(self):
        u = URL.parse("ch:arm64/mysql")
        self.assertEqual(u, URL(Schema.CHARM_HUB, name="mysql", architecture="arm64"))

    def test_parse_charmhub_with_no_series_arch(self):
        u = URL.parse("ch:mysql")
        self.assertEqual(u, URL(Schema.CHARM_HUB, name="mysql"))

    def test_parse_v2_revision(self):
        u = URL.parse("ch:mysql-1")
        self.assertEqual(u, URL(Schema.CHARM_HUB, name="mysql", revision=1))

    def test_parse_v2_large_revision(self):
        u = URL.parse("ch:mysql-12345")
        self.assertEqual(u, URL(Schema.CHARM_HUB, name="mysql", revision=12345))
