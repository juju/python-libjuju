# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import unittest

from juju.origin import Channel, Origin, Platform, Risk, Source


class TestRisk(unittest.TestCase):
    def test_valid_risk(self):
        self.assertTrue(Risk.valid("stable"))

    def test_invalid_risk(self):
        self.assertFalse(Risk.valid("maybe"))


class TestChannel(unittest.TestCase):
    def test_parse_risk_only(self):
        ch = Channel.parse("stable")
        self.assertEqual(ch, Channel(None, "stable"))

    def test_parse_track_only(self):
        ch = Channel.parse("2.0.1")
        self.assertEqual(ch, Channel("2.0.1", "stable"))

    def test_parse(self):
        ch = Channel.parse("latest/stable")
        self.assertEqual(ch, Channel("latest", "stable"))

    def test_parse_numeric(self):
        ch = Channel.parse("2.0.7/stable")
        self.assertEqual(ch, Channel("2.0.7", "stable"))

    def test_parse_then_normalize(self):
        ch = Channel.parse("latest/stable").normalize()
        self.assertEqual(ch, Channel("latest", "stable"))

    def test_str_risk_only(self):
        ch = Channel.parse("stable")
        self.assertEqual(str(ch), "stable")

    def test_str_track_only(self):
        ch = Channel.parse("2.0.1")
        self.assertEqual(str(ch), "2.0.1/stable")

    def test_str(self):
        ch = Channel.parse("latest/stable")
        self.assertEqual(str(ch), "latest/stable")

    def test_str_numeric(self):
        ch = Channel.parse("2.0.7/stable")
        self.assertEqual(str(ch), "2.0.7/stable")

    def test_str_then_normalize(self):
        ch = Channel.parse("latest/stable").normalize()
        self.assertEqual(str(ch), "latest/stable")


class TestPlatform(unittest.TestCase):
    def test_parse_arch_only(self):
        p = Platform.parse("architecture")
        self.assertEqual(p, Platform("architecture"))

    def test_parse_arch_and_series(self):
        p = Platform.parse("architecture/series")
        self.assertEqual(p, Platform("architecture", "series"))

    def test_parse(self):
        p = Platform.parse("architecture/os/series")
        self.assertEqual(p, Platform("architecture", "series", "os"))

    def test_parse_with_unknowns(self):
        p = Platform.parse("architecture/unknown/unknown")
        self.assertEqual(p, Platform("architecture", "unknown", "unknown"))

    def test_parse_with_unknowns_after_normalize(self):
        p = Platform.parse("architecture/unknown/unknown").normalize()
        self.assertEqual(p, Platform("architecture"))

    def test_str_arch_only(self):
        p = Platform.parse("architecture")
        self.assertEqual(str(p), "architecture")

    def test_str_arch_and_series(self):
        p = Platform.parse("architecture/series")
        self.assertEqual(str(p), "architecture/series")

    def test_str(self):
        p = Platform.parse("architecture/os/series")
        self.assertEqual(str(p), "architecture/os/series")


class TestOrigin(unittest.TestCase):
    def test_origin(self):
        ch = Channel.parse("latest/stable")
        p = Platform.parse("amd64/ubuntu/focal")

        o = Origin(Source.CHARM_HUB, ch, p)
        self.assertEqual(str(o), "origin using source charm-hub for channel latest/stable and platform amd64/ubuntu/focal")
