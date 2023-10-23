# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import unittest

from juju.url import Schema, URL


class TestURLV1(unittest.TestCase):
    def test_parse_charmstore(self):
        u = URL.parse("cs:mysql")
        self.assertEqual(u, URL(Schema.CHARM_STORE, name="mysql"))

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

    schema = Schema.CHARM_HUB

    def test_parse_charmhub(self):
        u = URL.parse(f"{self.schema}:arm64/bionic/mysql-1")
        self.assertEqual(u, URL(self.schema, name="mysql", architecture="arm64", series="bionic", revision=1))

    def test_parse_charmhub_with_no_series(self):
        u = URL.parse(f"{self.schema}:arm64/mysql")
        self.assertEqual(u, URL(self.schema, name="mysql", architecture="arm64"))

    def test_parse_charmhub_with_no_series_arch(self):
        u = URL.parse(f"{self.schema}:mysql")
        self.assertEqual(u, URL(self.schema, name="mysql"))

    def test_parse_v2_revision(self):
        u = URL.parse(f"{self.schema}:mysql-1")
        self.assertEqual(u, URL(self.schema, name="mysql", revision=1))

    def test_parse_v2_large_revision(self):
        u = URL.parse(f"{self.schema}:mysql-12345")
        self.assertEqual(u, URL(self.schema, name="mysql", revision=12345))

    def test_parse_v2_without_store(self):
        u = URL.parse("mysql-1", default_store=self.schema)
        self.assertEqual(u, URL(self.schema, name="mysql", revision=1))


class TestURLLocal(TestURLV2):
    schema = Schema.LOCAL
