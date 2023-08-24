# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from pathlib import Path
import unittest
from unittest import mock
from mock import patch, Mock, ANY

import yaml

from juju.bundle import (
    AddApplicationChange,
    AddCharmChange,
    AddMachineChange,
    AddRelationChange,
    AddUnitChange,
    BundleHandler,
    ChangeSet,
    ConsumeOfferChange,
    CreateOfferChange,
    ExposeChange,
    ScaleChange,
    SetAnnotationsChange,
)
from juju import charmhub
from juju.client import client
from toposort import CircularDependencyError


class TestChangeSet(unittest.TestCase):

    def test_sort_empty_changes(self):
        changeset = ChangeSet([])
        result = changeset.sorted()

        self.assertEqual(len(result), 0)

    def test_sort_changes(self):
        a = client.BundleChange(id_="a", requires=["b"])
        b = client.BundleChange(id_="b", requires=[])

        changeset = ChangeSet([a, b])
        result = changeset.sorted()

        self.assertEqual(len(result), 2)
        self.assertEqual(result, [b, a])

    def test_sort_complex_changes(self):
        a = client.BundleChange(id_="a", requires=[])
        b = client.BundleChange(id_="b", requires=["b"])
        c = client.BundleChange(id_="c", requires=["a", "d"])
        d = client.BundleChange(id_="d", requires=["a"])
        e = client.BundleChange(id_="e", requires=["a", "d", "c", "b"])
        f = client.BundleChange(id_="f", requires=["e", "d", "c"])

        changeset = ChangeSet([a, b, c, d, e, f])
        result = changeset.sorted()

        self.assertEqual(len(result), 6)
        self.assertEqual(result, [a, b, d, c, e, f])

    def test_sort_causes_circular_error(self):
        a = client.BundleChange(id_="a", requires=["b"])
        b = client.BundleChange(id_="b", requires=["a"])

        changeset = ChangeSet([a, b])
        self.assertRaises(CircularDependencyError, changeset.sorted)


class TestAddApplicationChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("deploy", AddApplicationChange.method())

    def test_dict_params(self):
        change = AddApplicationChange(1, [], params={"charm": "charm",
                                                     "series": "series",
                                                     "application": "application",
                                                     "options": "options",
                                                     "constraints": "constraints",
                                                     "storage": "storage",
                                                     "endpoint-bindings": "endpoint_bindings",
                                                     "resources": "resources",
                                                     "devices": "devices",
                                                     "num-units": "num_units",
                                                     "channel": "channel"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "charm": "charm",
                          "series": "series",
                          "application": "application",
                          "options": "options",
                          "constraints": "constraints",
                          "storage": "storage",
                          "endpoint_bindings": "endpoint_bindings",
                          "resources": "resources",
                          "devices": "devices",
                          "num_units": "num_units",
                          "channel": "channel"}, change.__dict__)

    def test_dict_params_missing_data(self):
        change = AddApplicationChange(1, [], params={"charm": "charm",
                                                     "series": "series",
                                                     "application": "application",
                                                     "options": "options",
                                                     "constraints": "constraints",
                                                     "storage": "storage"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "charm": "charm",
                          "series": "series",
                          "application": "application",
                          "options": "options",
                          "constraints": "constraints",
                          "storage": "storage",
                          "endpoint_bindings": None,
                          "resources": None,
                          "devices": None,
                          "num_units": None,
                          "channel": None}, change.__dict__)


class TestAddApplicationChangeRun:

    async def test_run_with_charmhub_charm(self, event_loop):
        change = AddApplicationChange(1, [], params={"charm": "charm",
                                                     "series": "series",
                                                     "application": "application",
                                                     "options": "options",
                                                     "constraints": "constraints",
                                                     "storage": "storage",
                                                     "endpoint-bindings": "endpoint_bindings",
                                                     "resources": "resources",
                                                     "devices": "devices",
                                                     "num-units": "num_units",
                                                     "channel": "channel"})

        model = Mock()
        model._deploy = mock.AsyncMock(return_value=None)
        model._add_charmhub_resources = mock.AsyncMock(return_value=["resource1"])
        model.applications = {}

        context = Mock()
        context.resolve.return_value = "ch:charm1"
        context.origins = {"ch:charm1": Mock()}
        context.trusted = False
        context.model = model

        info_func = mock.AsyncMock(return_value=["12345", "name"])

        with patch.object(charmhub.CharmHub, 'get_charm_id', info_func):
            result = await change.run(context)
        assert result == "application"

        model._deploy.assert_called_once()
        model._deploy.assert_called_with(charm_url="ch:charm1",
                                         application="application",
                                         series="series",
                                         config="options",
                                         constraints="constraints",
                                         endpoint_bindings="endpoint_bindings",
                                         resources=["resource1"],
                                         storage="storage",
                                         devices="devices",
                                         channel="channel",
                                         charm_origin=ANY,
                                         num_units="num_units")

    async def test_run_with_charmhub_charm_no_channel(self, event_loop):
        """Test to verify if when the given channel is None, the channel defaults to "local/stable", which
            is the default channel value for the Charm Hub
        """
        change = AddApplicationChange(1, [], params={"charm": "charm",
                                                     "series": "series",
                                                     "application": "application",
                                                     "options": "options",
                                                     "constraints": "constraints",
                                                     "storage": "storage",
                                                     "endpoint-bindings": "endpoint_bindings",
                                                     "resources": "resources",
                                                     "devices": "devices",
                                                     "num-units": "num_units",
                                                     "channel": None
                                                     })

        model = Mock()
        model._deploy = mock.AsyncMock(return_value=None)
        model._add_charmhub_resources = mock.AsyncMock(return_value=["resource1"])
        model.applications = {}

        context = Mock()
        context.resolve.return_value = "ch:charm1"
        context.origins = {"ch:charm1": {"latest/stable": Mock()}}
        context.trusted = False
        context.model = model

        info_func = mock.AsyncMock(return_value=["12345", "name"])

        with patch.object(charmhub.CharmHub, 'get_charm_id', info_func):
            result = await change.run(context)
        assert result == "application"

        model._deploy.assert_called_once()
        model._deploy.assert_called_with(charm_url="ch:charm1",
                                         application="application",
                                         series="series",
                                         config="options",
                                         constraints="constraints",
                                         endpoint_bindings="endpoint_bindings",
                                         resources=["resource1"],
                                         storage="storage",
                                         devices="devices",
                                         channel="latest/stable",
                                         charm_origin=ANY,
                                         num_units="num_units")

    async def test_run_local(self, event_loop):
        change = AddApplicationChange(1, [], params={"charm": "local:charm",
                                                     "series": "series",
                                                     "application": "application",
                                                     "options": "options",
                                                     "constraints": "constraints",
                                                     "storage": "storage",
                                                     "endpoint-bindings": "endpoint_bindings",
                                                     "devices": "devices",
                                                     "num-units": "num_units"})

        model = mock.Mock()
        model._deploy = mock.AsyncMock(return_value=None)
        model.applications = {}

        context = mock.Mock()
        context.resolve.return_value = "local:charm1"
        context.trusted = False
        context.model = model
        context.bundle = {"applications": {}}

        result = await change.run(context)
        assert result == "application"

        model._deploy.assert_called_once()
        model._deploy.assert_called_with(charm_url="local:charm1",
                                         application="application",
                                         series="series",
                                         config="options",
                                         constraints="constraints",
                                         endpoint_bindings="endpoint_bindings",
                                         resources={},
                                         storage="storage",
                                         devices="devices",
                                         num_units="num_units",
                                         channel="",
                                         charm_origin=ANY)

    async def test_run_no_series(self, event_loop):
        change = AddApplicationChange(1, [], params={"charm": "ch:charm1",
                                                     "series": "",
                                                     "application": "application",
                                                     "options": "options",
                                                     "constraints": "constraints",
                                                     "storage": "storage",
                                                     "endpoint-bindings": "endpoint_bindings",
                                                     "resources": "resources",
                                                     "devices": "devices",
                                                     "num-units": "num_units",
                                                     "channel": "channel"})

        model = mock.Mock()
        model._deploy = mock.AsyncMock(return_value=None)
        model._add_charmhub_resources = mock.AsyncMock(return_value=["resource1"])
        model.applications = {}

        context = mock.Mock()
        context.resolve.return_value = "ch:charm1"
        context.trusted = False
        context.model = model
        context.bundle = {"bundle": "kubernetes"}

        result = await change.run(context)
        assert result == "application"

        model._add_charmhub_resources.assert_called_once()

        model._deploy.assert_called_once()
        model._deploy.assert_called_with(charm_url="ch:charm1",
                                         application="application",
                                         series=None,
                                         config="options",
                                         constraints="constraints",
                                         endpoint_bindings="endpoint_bindings",
                                         resources=["resource1"],
                                         storage="storage",
                                         devices="devices",
                                         channel="channel",
                                         charm_origin=ANY,
                                         num_units="num_units")

        # confirm that it's idempotent
        model.applications = {"application": None}
        result = await change.run(context)
        assert result == "application"
        model._add_charmhub_resources.assert_called_once()
        model._deploy.assert_called_once()


class TestAddCharmChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("addCharm", AddCharmChange.method())

    def test_dict_params(self):
        change = AddCharmChange(1, [], params={"charm": "charm",
                                               "series": "series",
                                               "channel": "channel",
                                               "architecture": "architecture"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "charm": "charm",
                          "series": "series",
                          "channel": "channel",
                          "architecture": "architecture"}, change.__dict__)

    def test_dict_params_missing_data(self):
        change = AddCharmChange(1, [], params={"charm": "charm",
                                               "series": "series"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "charm": "charm",
                          "series": "series",
                          "channel": None,
                          "architecture": None}, change.__dict__)


class TestAddCharmChangeRun:

    async def test_run(self, event_loop):
        change = AddCharmChange(1, [], params={"charm": "ch:charm",
                                               "series": "jammy",
                                               "channel": "channel"})

        charms_facade = mock.Mock()
        charms_facade.AddCharm = mock.AsyncMock(return_value=None)

        model = mock.Mock()
        model._add_charm = mock.AsyncMock(return_value=None)
        model._resolve_architecture = mock.AsyncMock(return_value=None)
        model._resolve_charm = mock.AsyncMock(return_value=("entity_id",
                                                            None))

        context = mock.Mock()

        context.charms_facade = charms_facade
        context.origins = {}
        context.model = model

        result = await change.run(context)
        assert result == "entity_id"


class TestAddMachineChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("addMachines", AddMachineChange.method())

    def test_dict_params(self):
        change = AddMachineChange(1, [], params={"series": "series",
                                                 "constraints": "constraints",
                                                 "container-type": "container_type",
                                                 "parent-id": "parent_id"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "series": "series",
                          "constraints": "constraints",
                          "container_type": "container_type",
                          "parent_id": "parent_id"}, change.__dict__)

    def test_dict_params_missing_data(self):
        change = AddMachineChange(1, [], params={"series": "series",
                                                 "constraints": "constraints",
                                                 "container-type": "container_type"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "series": "series",
                          "constraints": "constraints",
                          "container_type": "container_type",
                          "parent_id": None}, change.__dict__)


class TestAddMachineChangeRun:

    async def test_run(self, event_loop):
        change = AddMachineChange(1, [], params={"series": "series",
                                                 "constraints": "cores=1",
                                                 "container-type": "container_type",
                                                 "parent-id": "parent_id"})

        machines = [client.AddMachinesResult(machine="machine1")]

        machine_manager_facade = mock.Mock()
        machine_manager_facade.AddMachines = mock.AsyncMock(return_value=client.AddMachinesResults(machines))

        context = mock.Mock()
        context.resolve.return_value = "parent_id1"
        context.machine_manager_facade = machine_manager_facade

        result = await change.run(context)
        assert result == "machine1"

        machine_manager_facade.AddMachines.assert_called_once()
        machine_manager_facade.AddMachines.assert_called_with(params=[client.AddMachineParams(series="series",
                                                                                              constraints="{\"cores\":1}",
                                                                                              container_type="container_type",
                                                                                              parent_id="parent_id1",
                                                                                              jobs=["JobHostUnits"])])


class TestAddRelationChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("addRelation", AddRelationChange.method())

    def test_dict_params(self):
        change = AddRelationChange(1, [], params={"endpoint1": "endpoint1",
                                                  "endpoint2": "endpoint2"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "endpoint1": "endpoint1",
                          "endpoint2": "endpoint2"}, change.__dict__)

    def test_dict_params_missing_data(self):
        change = AddRelationChange(1, [], params={"endpoint1": "endpoint1"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "endpoint1": "endpoint1",
                          "endpoint2": None}, change.__dict__)


class TestAddRelationChangeRun:
    async def test_run(self, event_loop):
        change = AddRelationChange(1, [], params={"endpoint1": "endpoint1",
                                                  "endpoint2": "endpoint2"})

        rel1 = mock.Mock(name="rel1", **{"matches.return_value": False})
        rel2 = mock.Mock(name="rel2", **{"matches.return_value": True})

        model = mock.Mock()
        model.relate = mock.AsyncMock(return_value=rel2)

        context = mock.Mock()
        context.resolve_relation = mock.Mock(side_effect=['endpoint_1', 'endpoint_2'])
        context.model = model
        model.relations = [rel1]

        result = await change.run(context)
        assert result is rel2

        model.relate.assert_called_once()
        model.relate.assert_called_with("endpoint_1", "endpoint_2")

        # confirm that it's idempotent
        context.resolve_relation = mock.Mock(side_effect=['endpoint_1', 'endpoint_2'])
        model.relate.reset_mock()
        model.relate.return_value = None
        model.relations = [rel1, rel2]
        result = await change.run(context)
        assert result is rel2
        assert not model.relate.called


class TestAddUnitChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("addUnit", AddUnitChange.method())

    def test_dict_params(self):
        change = AddUnitChange(1, [], params={"application": "application",
                                              "to": "to"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application",
                          "to": "to"}, change.__dict__)

    def test_dict_params_missing_data(self):
        change = AddUnitChange(1, [], params={"application": "application"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application",
                          "to": None}, change.__dict__)


class MockModel:

    def __init__(self, app):
        self.app = app

    @property
    def applications(self):
        return self.app


class TestAddUnitChangeRun:

    async def test_run(self, event_loop):
        change = AddUnitChange(1, [], params={"application": "application",
                                              "to": "to"})

        app = mock.Mock()
        app.add_unit = mock.AsyncMock(return_value="unit1")

        model = MockModel({"application1": app})

        context = mock.Mock()
        context.resolve = mock.Mock(side_effect=['application1', 'to1'])
        context._units_by_app = {}
        context.model = model

        result = await change.run(context)
        assert result == "unit1"

        model.applications["application1"].add_unit.assert_called_once()
        model.applications["application1"].add_unit.assert_called_with(count=1, to="to1")


class TestCreateOfferChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("createOffer", CreateOfferChange.method())

    def test_dict_params(self):
        change = CreateOfferChange(1, [], params={"application": "application",
                                                  "endpoints": "endpoints",
                                                  "offer-name": "offer_name"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application",
                          "endpoints": "endpoints",
                          "offer_name": "offer_name"}, change.__dict__)

    def test_dict_params_missing_data(self):
        change = CreateOfferChange(1, [], params={"application": "application",
                                                  "endpoints": "endpoints"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application",
                          "endpoints": "endpoints",
                          "offer_name": None}, change.__dict__)


class TestCreateOfferChangeRun:

    async def test_run(self, event_loop):
        change = CreateOfferChange(1, [], params={"application": "application",
                                                  "endpoints": ["endpoints"],
                                                  "offer-name": "offer_name"})

        model = mock.Mock()
        model.create_offer = mock.AsyncMock(return_value=None)

        context = mock.Mock()
        context.resolve = mock.Mock(side_effect=['application1'])
        context.model = model

        result = await change.run(context)
        assert result is None

        model.create_offer.assert_called_once()
        model.create_offer.assert_called_with("endpoints",
                                              offer_name="offer_name",
                                              application_name="application1")


class TestConsumeOfferChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("consumeOffer", ConsumeOfferChange.method())

    def test_dict_params(self):
        change = ConsumeOfferChange(1, [], params={"url": "url",
                                                   "application-name": "application_name"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "url": "url",
                          "application_name": "application_name"}, change.__dict__)

    def test_dict_params_missing_data(self):
        change = ConsumeOfferChange(1, [], params={"url": "url"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "url": "url",
                          "application_name": None}, change.__dict__)


class TestConsumeOfferChangeRun:

    async def test_run(self, event_loop):
        change = ConsumeOfferChange(1, [], params={"url": "url",
                                                   "application-name": "application_name"})

        model = mock.Mock()
        model.consume = mock.AsyncMock(return_value=None)

        context = mock.Mock()
        context.resolve = mock.Mock(side_effect=['application1'])
        context.model = model

        result = await change.run(context)
        assert result is None

        model.consume.assert_called_once()
        model.consume.assert_called_with("url",
                                         application_alias="application1")


class TestExposeChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("expose", ExposeChange.method())

    def test_dict_params(self):
        change = ExposeChange(1, [], params={"application": "application"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application",
                          "exposed_endpoints": None}, change.__dict__)

    def test_dict_params_missing_data(self):
        change = ExposeChange(1, [], params={})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": None,
                          "exposed_endpoints": None}, change.__dict__)

    def test_dict_params_with_exposed_endpoints_data(self):
        params = {
            "application": "application",
            "exposed-endpoints": {
                "": {
                    "to-spaces": ["alpha"],
                    "to-cidrs": ["10.0.0.0/24"]
                },
                "foo": {
                    "to-spaces": ["alien"],
                    "to-cidrs": ["0.0.0.0/0", "::/0"]
                }
            }
        }
        change = ExposeChange(1, [], params=params)
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application",
                          "exposed_endpoints": {
                              "": {
                                  "to-spaces": ["alpha"],
                                  "to-cidrs": ["10.0.0.0/24"]
                              },
                              "foo": {
                                  "to-spaces": ["alien"],
                                  "to-cidrs": ["0.0.0.0/0", "::/0"]
                              }
                          }}, change.__dict__)


class TestExposeChangeRun:

    async def test_run(self, event_loop):
        params = {
            "application": "application",
            "exposed-endpoints": {
                "": {
                    "to-spaces": ["alpha"],
                    "to-cidrs": ["10.0.0.0/24"]
                },
                "foo": {
                    "to-spaces": ["alien"],
                    "to-cidrs": ["0.0.0.0/0", "::/0"]
                }
            }
        }
        change = ExposeChange(1, [], params=params)

        app = mock.Mock()
        app.expose = mock.AsyncMock(return_value=None)

        model = MockModel({"application1": app})

        context = mock.Mock()
        context.resolve = mock.Mock(side_effect=['application1'])
        context.model = model

        result = await change.run(context)
        assert result is None

        model.applications["application1"].expose.assert_called_once()
        model.applications["application1"].expose.assert_called_with({
            "": {
                "to-spaces": ["alpha"],
                "to-cidrs": ["10.0.0.0/24"]
            },
            "foo": {
                "to-spaces": ["alien"],
                "to-cidrs": ["0.0.0.0/0", "::/0"]
            }
        })


class TestScaleChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("scale", ScaleChange.method())

    def test_dict_params(self):
        change = ScaleChange(1, [], params={"application": "application",
                                            "scale": "scale"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application",
                          "scale": "scale"}, change.__dict__)

    def test_dict_params_missing_data(self):
        change = ScaleChange(1, [], params={"application": "application"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application",
                          "scale": None}, change.__dict__)


class TestScaleChangeRun:

    async def test_run(self, event_loop):
        change = ScaleChange(1, [], params={"application": "application",
                                            "scale": 1})

        app = mock.Mock()
        app.scale = mock.AsyncMock(return_value=None)

        model = MockModel({"application1": app})

        context = mock.Mock()
        context.resolve = mock.Mock(side_effect=['application1'])
        context.model = model

        result = await change.run(context)
        assert result is None

        model.applications["application1"].scale.assert_called_once()
        model.applications["application1"].scale.assert_called_with(scale=1)


class TestSetAnnotationsChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("setAnnotations", SetAnnotationsChange.method())

    def test_dict_params(self):
        change = SetAnnotationsChange(1, [], params={"id": "id",
                                                     "entity-type": "entity_type",
                                                     "annotations": "annotations"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "id": "id",
                          "entity_type": "entity_type",
                          "annotations": "annotations"}, change.__dict__)

    def test_dict_params_missing_data(self):
        change = SetAnnotationsChange(1, [], params={"id": "id",
                                                     "entity-type": "entity_type"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "id": "id",
                          "entity_type": "entity_type",
                          "annotations": None}, change.__dict__)


class TestSetAnnotationsChangeRun:

    async def test_run(self, event_loop):
        change = SetAnnotationsChange(1, [], params={"id": "id",
                                                     "entity-type": "entity_type",
                                                     "annotations": "annotations"})

        entity = mock.Mock()
        entity.set_annotations = mock.AsyncMock(return_value="annotations1")

        state = mock.Mock()
        state.get_entity = mock.Mock(return_value=entity)

        model = mock.Mock()
        model.state = state

        context = mock.Mock()
        context.resolve = mock.Mock(side_effect=['application1'])
        context.model = model

        result = await change.run(context)
        assert result == "annotations1"

        entity.set_annotations.assert_called_once()
        entity.set_annotations.assert_called_with("annotations")


class TestBundleHandler:
    async def test_fetch_plan_local_k8s_bundle(self, event_loop):
        class AsyncMock(mock.MagicMock):
            async def __call__(self, *args, **kwargs):
                return super(AsyncMock, self).__call__(*args, **kwargs)

        bundle_dir = Path("tests/bundle")
        charm_dir_1 = "../integration/oci-image-charm"
        charm_dir_2 = "../integration/oci-image-charm-no-series"
        charm_path_1 = str((bundle_dir / charm_dir_1).resolve())
        charm_path_2 = str((bundle_dir / charm_dir_2).resolve())
        bundle = {
            "bundle": "kubernetes",
            "applications": {
                "oci-image-charm": {
                    "charm": charm_dir_1,
                    "resources": {"oci-image": "ubuntu:latest"}
                },
                "oci-image-charm-2": {
                    "charm": charm_dir_2,
                    "resources": {"oci-image": "ubuntu:latest"}
                },
                "oci-image-charm-3": {
                    "charm": charm_dir_2,
                    "resources": {"oci-image": "ubuntu:latest"}
                }
            }
        }

        connection_mock = mock.Mock()
        connection_mock.facades = {
            "Bundle": 17,
            "Client": 17,
            "Application": 17,
            "Annotations": 17,
            "MachineManager": 17,
        }
        model = mock.Mock()
        model.units = {}
        model.add_local_charm_dir = AsyncMock()
        model.add_local_charm_dir.return_value = "charm_uri"
        model.connection.return_value = connection_mock
        model.get_config = AsyncMock()
        default_series = mock.Mock()
        default_series.value = "focal"
        model_config = {"default-series": default_series}
        model.get_config.return_value = model_config
        model.add_local_resources = AsyncMock()
        model.add_local_resources.return_value = {"oci-image": "id"}
        handler = BundleHandler(model)
        handler.bundle = bundle

        bundle = await handler._handle_local_charms(bundle, bundle_dir)

        m1 = mock.call(
            "oci-image-charm",
            "charm_uri",
            yaml.load(Path("tests/integration/oci-image-charm/metadata.yaml").read_text(), Loader=yaml.FullLoader),
            resources={"oci-image": "ubuntu:latest"},
        )

        m2 = mock.call(
            "oci-image-charm-2",
            "charm_uri",
            yaml.load(Path("tests/integration/oci-image-charm-no-series/metadata.yaml").read_text(), Loader=yaml.FullLoader),
            resources={"oci-image": "ubuntu:latest"},
        )

        m3 = mock.call(
            "oci-image-charm-3",
            "charm_uri",
            yaml.load(Path("tests/integration/oci-image-charm-no-series/metadata.yaml").read_text(), Loader=yaml.FullLoader),
            resources={"oci-image": "ubuntu:latest"},
        )

        m_add_local_resources_calls = model.add_local_resources.mock_calls
        assert len(m_add_local_resources_calls) == 3
        assert m1 in m_add_local_resources_calls and \
            m2 in m_add_local_resources_calls and \
            m3 in m_add_local_resources_calls

        mc_1 = mock.call(charm_path_1, "focal")
        mc_2 = mock.call(charm_path_2, "focal")
        mc_3 = mock.call(charm_path_2, "focal")

        m_add_local_charm_dir_calls = model.add_local_charm_dir.mock_calls
        assert len(m_add_local_charm_dir_calls) == 3
        assert mc_1 in m_add_local_charm_dir_calls and \
            mc_2 in m_add_local_charm_dir_calls and \
            mc_3 in m_add_local_charm_dir_calls

        assert bundle["applications"]["oci-image-charm"]["resources"]["oci-image"] == "id"
