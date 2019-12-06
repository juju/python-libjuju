import unittest
from unittest import mock

import pytest
from juju.bundle import (AddApplicationChange, AddCharmChange,
                         AddMachineChange, AddRelationChange, AddUnitChange,
                         ChangeSet, ConsumeOfferChange, CreateOfferChange,
                         ExposeChange, ScaleChange, SetAnnotationsChange)
from juju.client import client
from toposort import CircularDependencyError

from .. import base


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

    def test_list_params_juju_2_4(self):
        change = AddApplicationChange(1, [], params=["charm",
                                                     "series",
                                                     "application",
                                                     "options",
                                                     "constraints",
                                                     {"db": "pool,1,1GB"},
                                                     "endpoint_bindings",
                                                     "resources"])
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "charm": "charm",
                          "series": "series",
                          "application": "application",
                          "options": "options",
                          "constraints": "constraints",
                          "storage": {"db": {"pool": "pool", "count": 1, "size": 1024}},
                          "endpoint_bindings": "endpoint_bindings",
                          "resources": "resources",
                          "devices": None,
                          "num_units": None}, change.__dict__)

    def test_list_params_juju_2_5(self):
        change = AddApplicationChange(1, [], params=["charm",
                                                     "series",
                                                     "application",
                                                     "options",
                                                     "constraints",
                                                     {"db": "pool,1,1GB"},
                                                     {"gpu": "1,gpu,attr1=a;attr2=b"},
                                                     "endpoint_bindings",
                                                     "resources",
                                                     "num_units"])
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "charm": "charm",
                          "series": "series",
                          "application": "application",
                          "options": "options",
                          "constraints": "constraints",
                          "storage": {"db": {"pool": "pool", "count": 1, "size": 1024}},
                          "endpoint_bindings": "endpoint_bindings",
                          "resources": "resources",
                          "devices": {"gpu": {"type": "gpu", "count": 1, "attributes": {"attr1": "a", "attr2": "b"}}},
                          "num_units": "num_units"}, change.__dict__)

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
                                                     "num-units": "num_units"})
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
                          "num_units": "num_units"}, change.__dict__)

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
                          "num_units": None}, change.__dict__)


class TestAddApplicationChangeRun:

    @pytest.mark.asyncio
    async def test_run(self, event_loop):
        change = AddApplicationChange(1, [], params={"charm": "charm",
                                                     "series": "series",
                                                     "application": "application",
                                                     "options": "options",
                                                     "constraints": "constraints",
                                                     "storage": "storage",
                                                     "endpoint-bindings": "endpoint_bindings",
                                                     "resources": "resources",
                                                     "devices": "devices",
                                                     "num-units": "num_units"})

        model = mock.Mock()
        model._deploy = base.AsyncMock(return_value=None)
        model._add_store_resources = base.AsyncMock(return_value=["resource1"])

        context = mock.Mock()
        context.resolve.return_value = "charm1"
        context.trusted = False
        context.model = model

        result = await change.run(context)
        assert result == "application"

        model._add_store_resources.assert_called_once()
        model._add_store_resources.assert_called_with("application",
                                                      "charm1",
                                                      overrides="resources")

        model._deploy.assert_called_once()
        model._deploy.assert_called_with(charm_url="charm1",
                                         application="application",
                                         series="series",
                                         config="options",
                                         constraints="constraints",
                                         endpoint_bindings="endpoint_bindings",
                                         resources=["resource1"],
                                         storage="storage",
                                         devices="devices",
                                         num_units="num_units")

    @pytest.mark.asyncio
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
        model._deploy = base.AsyncMock(return_value=None)

        context = mock.Mock()
        context.resolve.return_value = "local:charm1"
        context.trusted = False
        context.model = model

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
                                         num_units="num_units")


class TestAddCharmChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("addCharm", AddCharmChange.method())

    def test_list_params_juju_2_6(self):
        change = AddCharmChange(1, [], params=["charm",
                                               "series"])
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "charm": "charm",
                          "series": "series",
                          "channel": None}, change.__dict__)

    def test_list_params_juju_2_7(self):
        change = AddCharmChange(1, [], params=["charm",
                                               "series",
                                               "channel"])
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "charm": "charm",
                          "series": "series",
                          "channel": "channel"}, change.__dict__)

    def test_dict_params(self):
        change = AddCharmChange(1, [], params={"charm": "charm",
                                               "series": "series",
                                               "channel": "channel"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "charm": "charm",
                          "series": "series",
                          "channel": "channel"}, change.__dict__)

    def test_dict_params_missing_data(self):
        change = AddCharmChange(1, [], params={"charm": "charm",
                                               "series": "series"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "charm": "charm",
                          "series": "series",
                          "channel": None}, change.__dict__)


class TestAddCharmChangeRun:

    @pytest.mark.asyncio
    async def test_run(self, event_loop):
        change = AddCharmChange(1, [], params={"charm": "charm",
                                               "series": "series",
                                               "channel": "channel"})

        charmstore = mock.Mock()
        charmstore.entityId = base.AsyncMock(return_value="entity_id")

        client_facade = mock.Mock()
        client_facade.AddCharm = base.AsyncMock(return_value=None)

        context = mock.Mock()
        context.charmstore = charmstore
        context.client_facade = client_facade

        result = await change.run(context)
        assert result == "entity_id"

        charmstore.entityId.assert_called_once()
        charmstore.entityId.assert_called_with("charm")

        client_facade.AddCharm.assert_called_once()
        client_facade.AddCharm.assert_called_with(channel=None,
                                                  url="entity_id",
                                                  force=False)


class TestAddMachineChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("addMachines", AddMachineChange.method())

    def test_list_params(self):
        change = AddMachineChange(1, [], params=[{"series": "series",
                                                  "constraints": "constraints",
                                                  "containerType": "container_type",
                                                  "parentId": "parent_id"}])
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "series": "series",
                          "constraints": "constraints",
                          "container_type": "container_type",
                          "parent_id": "parent_id"}, change.__dict__)

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

    @pytest.mark.asyncio
    async def test_run(self, event_loop):
        change = AddMachineChange(1, [], params={"series": "series",
                                                 "constraints": "cores=1",
                                                 "container-type": "container_type",
                                                 "parent-id": "parent_id"})

        machines = [client.AddMachinesResult(machine="machine1")]

        client_facade = mock.Mock()
        client_facade.AddMachines = base.AsyncMock(return_value=client.AddMachinesResults(machines))

        context = mock.Mock()
        context.resolve.return_value = "parent_id1"
        context.client_facade = client_facade

        result = await change.run(context)
        assert result == "machine1"

        client_facade.AddMachines.assert_called_once()
        client_facade.AddMachines.assert_called_with(params=[client.AddMachineParams(series="series",
                                                                                     constraints="{\"cores\":1}",
                                                                                     container_type="container_type",
                                                                                     parent_id="parent_id1",
                                                                                     jobs=["JobHostUnits"])])


class TestAddRelationChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("addRelation", AddRelationChange.method())

    def test_list_params(self):
        change = AddRelationChange(1, [], params=["endpoint1", "endpoint2"])
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "endpoint1": "endpoint1",
                          "endpoint2": "endpoint2"}, change.__dict__)

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

    @pytest.mark.asyncio
    async def test_run(self, event_loop):
        change = AddRelationChange(1, [], params={"endpoint1": "endpoint1",
                                                  "endpoint2": "endpoint2"})

        model = mock.Mock()
        model.add_relation = base.AsyncMock(return_value="relation1")

        context = mock.Mock()
        context.resolveRelation = mock.Mock(side_effect=['endpoint_1', 'endpoint_2'])
        context.model = model

        result = await change.run(context)
        assert result == "relation1"

        model.add_relation.assert_called_once()
        model.add_relation.assert_called_with("endpoint_1", "endpoint_2")


class TestAddUnitChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("addUnit", AddUnitChange.method())

    def test_list_params(self):
        change = AddUnitChange(1, [], params=["application", "to"])
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application",
                          "to": "to"}, change.__dict__)

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

    @pytest.mark.asyncio
    async def test_run(self, event_loop):
        change = AddUnitChange(1, [], params={"application": "application",
                                              "to": "to"})

        app = mock.Mock()
        app.add_unit = base.AsyncMock(return_value="unit1")

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

    def test_list_params(self):
        change = CreateOfferChange(1, [], params=["application", "endpoints", "offer_name"])
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application",
                          "endpoints": "endpoints",
                          "offer_name": "offer_name"}, change.__dict__)

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

    @pytest.mark.asyncio
    async def test_run(self, event_loop):
        change = CreateOfferChange(1, [], params={"application": "application",
                                                  "endpoints": ["endpoints"],
                                                  "offer-name": "offer_name"})

        model = mock.Mock()
        model.create_offer = base.AsyncMock(return_value=None)

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

    def test_list_params(self):
        change = ConsumeOfferChange(1, [], params=["url", "application_name"])
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "url": "url",
                          "application_name": "application_name"}, change.__dict__)

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

    @pytest.mark.asyncio
    async def test_run(self, event_loop):
        change = ConsumeOfferChange(1, [], params={"url": "url",
                                                   "application-name": "application_name"})

        model = mock.Mock()
        model.consume = base.AsyncMock(return_value=None)

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

    def test_list_params(self):
        change = ExposeChange(1, [], params=["application"])
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application"}, change.__dict__)

    def test_dict_params(self):
        change = ExposeChange(1, [], params={"application": "application"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application"}, change.__dict__)

    def test_dict_params_missing_data(self):
        change = ExposeChange(1, [], params={})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": None}, change.__dict__)


class TestExposeChangeRun:

    @pytest.mark.asyncio
    async def test_run(self, event_loop):
        change = ExposeChange(1, [], params={"application": "application"})

        app = mock.Mock()
        app.expose = base.AsyncMock(return_value=None)

        model = MockModel({"application1": app})

        context = mock.Mock()
        context.resolve = mock.Mock(side_effect=['application1'])
        context.model = model

        result = await change.run(context)
        assert result is None

        model.applications["application1"].expose.assert_called_once()


class TestScaleChange(unittest.TestCase):

    def test_method(self):
        self.assertEqual("scale", ScaleChange.method())

    def test_list_params(self):
        change = ScaleChange(1, [], params=["application", "scale"])
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "application": "application",
                          "scale": "scale"}, change.__dict__)

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

    @pytest.mark.asyncio
    async def test_run(self, event_loop):
        change = ScaleChange(1, [], params={"application": "application",
                                            "scale": 1})

        app = mock.Mock()
        app.scale = base.AsyncMock(return_value=None)

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

    def test_list_params(self):
        change = SetAnnotationsChange(1, [], params=["id", "entity_type", "annotations"])
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "id": "id",
                          "entity_type": "entity_type",
                          "annotations": "annotations"}, change.__dict__)

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

    @pytest.mark.asyncio
    async def test_run(self, event_loop):
        change = SetAnnotationsChange(1, [], params={"id": "id",
                                                     "entity-type": "entity_type",
                                                     "annotations": "annotations"})

        entity = mock.Mock()
        entity.set_annotations = base.AsyncMock(return_value="annotations1")

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
