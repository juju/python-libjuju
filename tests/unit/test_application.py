# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import asyncio
import unittest
from unittest import mock

from juju.application import Application, ExposedEndpoint, _refresh_origin
from juju.client import client
from juju.errors import JujuError
from juju.model import Model
from juju.origin import Source


class TestExposeApplication(unittest.IsolatedAsyncioTestCase):
    @mock.patch("juju.model.Model.connection")
    async def test_expose_with_exposed_endpoints_as_raw_dict(self, mock_conn):
        mock_facade_version = mock.MagicMock(return_value=13)
        mock_facade = mock.MagicMock(name="application_facade")
        mock_facade().Expose.return_value = asyncio.Future()
        mock_facade().Expose.return_value.set_result([])

        app = Application(entity_id="app-id", model=Model())
        app._facade = mock_facade
        app._facade_version = mock_facade_version

        # Check that if we pass a dict as would be the case when processing an
        # expose change, it gets correctly converted to ExposedEndpoint values,
        # validated and converted to a dictionary with the right format before
        # it gets passed to the facade.
        await app.expose(
            exposed_endpoints={
                "": {"expose-to-spaces": ["alpha"], "expose-to-cidrs": ["0.0.0.0/0"]}
            }
        )

        mock_facade().Expose.assert_called_once_with(
            application="app-id",
            exposed_endpoints={
                "": {"expose-to-spaces": ["alpha"], "expose-to-cidrs": ["0.0.0.0/0"]}
            },
        )

    @mock.patch("juju.model.Model.connection")
    async def test_expose_with_exposed_endpoints(self, mock_conn):
        mock_facade_version = mock.MagicMock(return_value=13)
        mock_facade = mock.MagicMock(name="application_facade")
        mock_facade().Expose.return_value = asyncio.Future()
        mock_facade().Expose.return_value.set_result([])

        app = Application(entity_id="app-id", model=Model())
        app._facade = mock_facade
        app._facade_version = mock_facade_version

        # Check that if we pass a dict with ExposedEndpoint values, they get
        # validated and converted to a dictionary with the right format before
        # it gets passed to the facade.
        await app.expose(
            exposed_endpoints={
                "": ExposedEndpoint(to_spaces=["alpha"], to_cidrs=["0.0.0.0/0"]),
                "x": ExposedEndpoint(to_spaces=["beta"]),
                "y": ExposedEndpoint(to_cidrs=["10.0.0.0/24"]),
            }
        )

        mock_facade().Expose.assert_called_once_with(
            application="app-id",
            exposed_endpoints={
                "": {"expose-to-spaces": ["alpha"], "expose-to-cidrs": ["0.0.0.0/0"]},
                "x": {
                    "expose-to-spaces": ["beta"],
                },
                "y": {
                    "expose-to-cidrs": ["10.0.0.0/24"],
                },
            },
        )

    @mock.patch("juju.model.Model.connection")
    async def test_expose_endpoints_on_older_controller(self, mock_conn):
        mock_facade_version = mock.MagicMock(return_value=12)
        mock_facade = mock.MagicMock(name="application_facade")
        mock_facade().Expose.return_value = asyncio.Future()
        mock_facade().Expose.return_value.set_result([])

        app = Application(entity_id="app-id", model=Model())
        app._facade = mock_facade
        app._facade_version = mock_facade_version

        # If we try to expose individual endpoints on an older controller
        # (app facade < 13) we should get an error back.

        # Case 1: exposed_endpoints includes an entry with a space list.
        with self.assertRaises(JujuError):
            await app.expose(
                exposed_endpoints={
                    "": ExposedEndpoint(to_spaces=["alpha"]),
                }
            )

        # Case 2: exposed_endpoints only includes the wildcard endpoints key
        # with a non-wildcard CIDR.
        with self.assertRaises(JujuError):
            await app.expose(
                exposed_endpoints={
                    "": ExposedEndpoint(to_cidrs=["0.0.0.0/0", "10.0.0.0/24"]),
                }
            )

        # Case 3: exposed_endpoints has a single entry for the
        # non-wildcard endpoint.
        with self.assertRaises(JujuError):
            await app.expose(
                exposed_endpoints={
                    "": ExposedEndpoint(to_cidrs=["0.0.0.0/0", "10.0.0.0/24"]),
                }
            )

        # Case 4: exposed_endpoints has multiple keys.
        with self.assertRaises(JujuError):
            await app.expose(
                exposed_endpoints={
                    "foo": ExposedEndpoint(to_cidrs=["0.0.0.0/0"]),
                    "bar": ExposedEndpoint(to_spaces=["alpha"]),
                }
            )

        # Check that we call the facade with the right arity.
        await app.expose()
        mock_facade().Expose.assert_called_once_with(application="app-id")


class TestUnExposeApplication(unittest.IsolatedAsyncioTestCase):
    @mock.patch("juju.model.Model.connection")
    async def test_unexpose_endpoints_on_older_controller(self, mock_conn):
        mock_facade_version = mock.MagicMock(return_value=12)
        mock_facade = mock.MagicMock(name="application_facade")
        mock_facade().Unexpose.return_value = asyncio.Future()
        mock_facade().Unexpose.return_value.set_result([])

        app = Application(entity_id="app-id", model=Model())
        app._facade = mock_facade
        app._facade_version = mock_facade_version

        # If we try to unexpose individual endpoints on an older controller
        # (app facade < 13) we should get an error back.
        with self.assertRaises(JujuError):
            await app.unexpose(exposed_endpoints=["outer", "inner"])

        # Check that we call the facade with the right arity.
        await app.unexpose()
        mock_facade().Unexpose.assert_called_once_with(application="app-id")

    @mock.patch("juju.model.Model.connection")
    async def test_unexpose_endpoints_on_29_controller(self, mock_conn):
        mock_facade_version = mock.MagicMock(return_value=13)
        mock_facade = mock.MagicMock(name="application_facade")
        mock_facade().Unexpose.return_value = asyncio.Future()
        mock_facade().Unexpose.return_value.set_result([])

        app = Application(entity_id="app-id", model=Model())
        app._facade = mock_facade
        app._facade_version = mock_facade_version

        await app.unexpose(exposed_endpoints=["alpha", "beta"])

        mock_facade().Unexpose.assert_called_once_with(
            application="app-id", exposed_endpoints=["alpha", "beta"]
        )


class TestRefreshApplication(unittest.IsolatedAsyncioTestCase):
    @mock.patch("juju.model.Model.connection")
    async def test_refresh_mutually_exclusive_kwargs(self, mock_conn):
        app = Application(entity_id="app-id", model=Model())
        with self.assertRaises(ValueError):
            await app.refresh(switch="charm1", revision=10)

        with self.assertRaises(ValueError):
            await app.refresh(switch="charm1", path="/path/to/charm2")

    def test_refresh_origin(self):
        current_origin = client.CharmOrigin(
            source=str(Source.CHARM_HUB),
            track="latest",
            risk="stable",
            revision=100,
            base=client.Base("24.04", "ubuntu"),
            architecture="amd64",
        )

        origin = _refresh_origin(current_origin, None, None)
        self.assertEqual(origin, current_origin)

        origin = _refresh_origin(current_origin, None, 101)
        self.assertEqual(origin.revision, 101)
        # Check source, base & arch do not change
        self.assertEqual(origin.source, current_origin.source)
        self.assertEqual(origin.base, current_origin.base)
        self.assertEqual(origin.architecture, current_origin.architecture)

        origin = _refresh_origin(current_origin, None, 0)
        self.assertEqual(origin.revision, 0)
        # Check source, base & arch do not change
        self.assertEqual(origin.source, current_origin.source)
        self.assertEqual(origin.base, current_origin.base)
        self.assertEqual(origin.architecture, current_origin.architecture)

        origin = _refresh_origin(current_origin, "12/edge", None)
        self.assertEqual(origin.track, "12")
        self.assertEqual(origin.risk, "edge")
        # Check source, base & arch do not change
        self.assertEqual(origin.source, current_origin.source)
        self.assertEqual(origin.base, current_origin.base)
        self.assertEqual(origin.architecture, current_origin.architecture)

    def test_refresh_origin_drops_id_hash(self):
        current_origin = client.CharmOrigin(
            source=str(Source.CHARM_HUB),
            track="latest",
            risk="stable",
            revision=100,
            base=client.Base("24.04", "ubuntu"),
            architecture="amd64",
            id_="id",
            hash_="hash",
        )

        origin = _refresh_origin(current_origin, None, None)
        self.assertIsNone(origin.id_)
        self.assertIsNone(origin.hash_)
