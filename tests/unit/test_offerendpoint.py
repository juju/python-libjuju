# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

#
# Test our offer endpoint parser
#

import unittest
from unittest import mock

from juju.controller import Controller
from juju.model import Model
from juju.offerendpoints import (
    LocalEndpoint,
    OfferEndpoints,
    OfferURL,
    ParseError,
    maybe_parse_offer_url_source,
    parse_local_endpoint,
    parse_offer_endpoint,
    parse_offer_url,
)


class TestOfferEndpoint(unittest.TestCase):
    def test_parse_offer_endpoint(self):
        cases = {
            "mysql:db": OfferEndpoints("mysql", ["db"]),
            "model/fred.mysql:db": OfferEndpoints(
                "mysql", ["db"], "model", "model/fred"
            ),
            "mysql:db,log": OfferEndpoints("mysql", ["db", "log"]),
        }
        for name, case in cases.items():
            self.assertEqual(parse_offer_endpoint(name), case)


class TestOfferURL(unittest.TestCase):
    def test_parse_offer_url(self):
        cases = {
            "controller:user/modelname.applicationname": OfferURL(
                source="controller",
                user="user",
                model="modelname",
                application="applicationname",
            ),
            "controller:user/modelname.applicationname:rel": OfferURL(
                source="controller",
                user="user",
                model="modelname",
                application="applicationname:rel",
            ),
            "modelname.applicationname": OfferURL(
                model="modelname", application="applicationname"
            ),
            "modelname.applicationname:rel": OfferURL(
                model="modelname", application="applicationname:rel"
            ),
            "/modelname.applicationname": OfferURL(
                model="modelname", application="applicationname"
            ),
            "/modelname.applicationname:rel": OfferURL(
                model="modelname", application="applicationname:rel"
            ),
            "user/modelname.applicationname": OfferURL(
                user="user", model="modelname", application="applicationname"
            ),
            "user/modelname.applicationname:rel": OfferURL(
                user="user", model="modelname", application="applicationname:rel"
            ),
        }
        for name, case in cases.items():
            self.assertEqual(parse_offer_url(name), case)

    def test_parse_offer_url_failures(self):
        cases = {
            "controller:modelname": "application offer URL is missing application",
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
        cases = {
            "name": ("", "name"),
            "name:app": ("", "name:app"),
            "name:app:rel": ("name", "app:rel"),
            "name:app:rel:other": ("name", "app:rel:other"),
        }
        for name, case in cases.items():
            self.assertEqual(maybe_parse_offer_url_source(name), case)


class TestLocalEndpoint(unittest.TestCase):
    def test_parse_local_endpoint(self):
        cases = {
            "applicationname": LocalEndpoint(application="applicationname"),
            "applicationname:relation": LocalEndpoint(
                application="applicationname", relation="relation"
            ),
        }
        for name, case in cases.items():
            self.assertEqual(parse_local_endpoint(name), case)

    def test_parse_local_endpoint_failures(self):
        cases = {
            ":applicationname": "endpoint :applicationname not valid",
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


class TestConsume(unittest.IsolatedAsyncioTestCase):
    @mock.patch.object(Model, "connection")
    @mock.patch.object(Controller, "disconnect")
    @mock.patch("juju.model._create_consume_args")
    @mock.patch("juju.client.client.ApplicationFacade.from_connection")
    async def test_external_controller_consume(
        self,
        mock_from_connection,
        mock_controller,
        mock_connection,
        mock_create_consume_args,
    ):
        """Test consuming an offer from an external controller.

        This would be better suited as an integration test however
        pylibjuju does not allow for bootstrapping of extra controllers.
        """
        mock_create_consume_args.return_value = None
        mock_connection.return_value = None

        mock_consume_details = mock.MagicMock()
        mock_consume_details.offer.offer_url = "user/offerer.app"
        mock_controller.get_consume_details = mock.AsyncMock(
            return_value=mock_consume_details
        )
        mock_controller.disconnect = mock.AsyncMock()

        mock_facade = mock.MagicMock()
        mock_from_connection.return_value = mock_facade

        mock_results = mock.MagicMock()
        mock_results.results = [mock.MagicMock()]
        mock_results.results[0].error = None
        mock_facade.Consume = mock.AsyncMock(return_value=mock_results)

        m = Model()
        m._get_source_api = mock.AsyncMock(return_value=mock_controller)

        # Test with an external controller.
        offer_url = "externalcontroller:user/offerer.app"
        await m.consume(offer_url)
        m._get_source_api.assert_called_once_with(parse_offer_url(offer_url))
        mock_controller.get_consume_details.assert_called_with("user/offerer.app")

        # Test with an external controller and controller_name arg.
        offer_url = "externalcontroller:user/offerer.app"
        await m.consume(offer_url, controller_name="externalcontroller")
        m._get_source_api.assert_called_with(parse_offer_url(offer_url))
        mock_controller.get_consume_details.assert_called_with("user/offerer.app")

        # Test with a local (mocked) controller.
        offer_url = "user/offerer.app"
        await m.consume(offer_url, controller=mock_controller)
        mock_controller.get_consume_details.assert_called_with("user/offerer.app")

        # Test with an external controller with just controller_name. This will
        # soon be deprecated.
        offer_url = "user/offerer.app"
        await m.consume(offer_url, controller_name="externalcontroller")
        m._get_source_api.assert_called_with(
            parse_offer_url("externalcontroller:user/offerer.app")
        )
        mock_controller.get_consume_details.assert_called_with("user/offerer.app")
