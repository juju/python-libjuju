import unittest

from juju.url import Schema, URL


class TestURLV1(unittest.TestCase):
    def test_parse_charmstore(self):
        u = URL.parse("cs:mysql")
        self.assertEqual(u, URL(Schema.CHARM_STORE, name="mysql"))

    def test_parse_local(self):
        u = URL.parse("local:mysql")
        self.assertEqual(u, URL(Schema.LOCAL, name="mysql"))

    def test_parse_v1_user(self):
        u = URL.parse("cs:~fred/mysql")
        self.assertEqual(u, URL(Schema.CHARM_STORE, name="mysql", user="fred"))

    def test_parse_v1_revision(self):
        u = URL.parse("cs:~fred/mysql-1")
        self.assertEqual(u, URL(Schema.CHARM_STORE, name="mysql", user="fred", revision=1))

    def test_parse_v1_large_revision(self):
        u = URL.parse("cs:~fred/mysql-12345")
        self.assertEqual(u, URL(Schema.CHARM_STORE, name="mysql", user="fred", revision=12345))

    def test_parse_v1_series(self):
        u = URL.parse("cs:~fred/bionic/mysql-1")
        self.assertEqual(u, URL(Schema.CHARM_STORE, name="mysql", user="fred", revision=1, series="bionic"))


class TestURLV2(unittest.TestCase):
    def test_parse_charmhub(self):
        u = URL.parse("ch:mysql")
        self.assertEqual(u, URL(Schema.CHARM_HUB, name="mysql"))

    def test_parse_v2_revision(self):
        u = URL.parse("ch:mysql-1")
        self.assertEqual(u, URL(Schema.CHARM_HUB, name="mysql", revision=1))

    def test_parse_v2_large_revision(self):
        u = URL.parse("ch:mysql-12345")
        self.assertEqual(u, URL(Schema.CHARM_HUB, name="mysql", revision=12345))
