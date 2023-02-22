#
# Test our offer endpoint parser
#

import unittest

from juju.offerendpoints import (LocalEndpoint, OfferEndpoints, OfferURL,
                                 ParseError, maybe_parse_offer_url_source,
                                 parse_local_endpoint, parse_offer_endpoint,
                                 parse_offer_url)


class TestOfferEndpoint(unittest.TestCase):

    def test_parse_offer_endpoint(self):

        cases = {"mysql:db": OfferEndpoints("mysql", ["db"]),
                 "model/fred.mysql:db": OfferEndpoints("mysql", ["db"], "model", "model/fred"),
                 "mysql:db,log": OfferEndpoints("mysql", ["db", "log"]),
                 }
        for name, case in cases.items():
            self.assertEqual(parse_offer_endpoint(name), case)


class TestOfferURL(unittest.TestCase):

    def test_parse_offer_url(self):
        cases = {"controller:user/modelname.applicationname": OfferURL(source="controller", user="user", model="modelname", application="applicationname"),
                 "controller:user/modelname.applicationname:rel": OfferURL(source="controller", user="user", model="modelname", application="applicationname:rel"),
                 "modelname.applicationname": OfferURL(model="modelname", application="applicationname"),
                 "modelname.applicationname:rel": OfferURL(model="modelname", application="applicationname:rel"),
                 "/modelname.applicationname": OfferURL(model="modelname", application="applicationname"),
                 "/modelname.applicationname:rel": OfferURL(model="modelname", application="applicationname:rel"),
                 "user/modelname.applicationname": OfferURL(user="user", model="modelname", application="applicationname"),
                 "user/modelname.applicationname:rel": OfferURL(user="user", model="modelname", application="applicationname:rel"),
                 }
        for name, case in cases.items():
            self.assertEqual(parse_offer_url(name), case)

    def test_parse_offer_url_failures(self):
        cases = {"controller:modelname": "application offer URL is missing application",
                 "controller:user/modelname": "application offer URL is missing application",
                 "modelname": "application offer URL is missing application",
                 "/user/modelname": "application offer URL is missing application",
                 "modelname.applicationname@bad": "application name applicationname@bad not valid",
                 "user[bad/model.application": "user name user[bad not valid",
                 "user/[badmodel.application": "model name [badmodel not valid",
                 }
        for name, case in cases.items():
            try:
                parse_offer_url(name)
            except ParseError as e:
                self.assertEqual(e.message, case)
            except Exception:
                raise

    def test_maybe_parse_offer_url_source(self):
        cases = {"name": ("", "name"),
                 "name:app": ("", "name:app"),
                 "name:app:rel": ("name", "app:rel"),
                 "name:app:rel:other": ("name", "app:rel:other"),
                 }
        for name, case in cases.items():
            self.assertEqual(maybe_parse_offer_url_source(name), case)


class TestLocalEndpoint(unittest.TestCase):

    def test_parse_local_endpoint(self):
        cases = {"applicationname": LocalEndpoint(application="applicationname"),
                 "applicationname:relation": LocalEndpoint(application="applicationname", relation="relation"),
                 }
        for name, case in cases.items():
            self.assertEqual(parse_local_endpoint(name), case)

    def test_parse_local_endpoint_failures(self):
        cases = {":applicationname": "endpoint :applicationname not valid",
                 "applicationname:": "endpoint applicationname: not valid",
                 "applicationname:user:relation": "endpoint applicationname:user:relation not valid",
                 "applicationname:_relation": "endpoint applicationname:_relation not valid",
                 "applicationname:0relation": "endpoint applicationname:0relation not valid",
                 }
        for name, case in cases.items():
            try:
                parse_local_endpoint(name)
            except ParseError as e:
                self.assertEqual(e.message, case)
            except Exception:
                raise
