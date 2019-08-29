import unittest

from juju.bundle import (AddApplicationChange, AddCharmChange,
                         AddMachineChange, AddRelationChange, AddUnitChange,
                         ChangeSet, ConsumeOfferChange, CreateOfferChange,
                         ExposeChange, ScaleChange, SetAnnotationsChange)
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

    def test_list_params_juju_2_4(self):
        change = AddApplicationChange(1, [], params=["charm",
                                                     "series",
                                                     "application",
                                                     "options",
                                                     "constraints",
                                                     "storage",
                                                     "endpoint_bindings",
                                                     "resources"])
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
                          "devices": None,
                          "num_units": None}, change.__dict__)

    def test_list_params_juju_2_5(self):
        change = AddApplicationChange(1, [], params=["charm",
                                                     "series",
                                                     "application",
                                                     "options",
                                                     "constraints",
                                                     "storage",
                                                     "endpoint_bindings",
                                                     "devices",
                                                     "resources",
                                                     "num_units"])
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
                                                   "application_name": "application_name"})
        self.assertEqual({"change_id": 1,
                          "requires": [],
                          "url": "url",
                          "application_name": "application_name"}, change.__dict__)


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
