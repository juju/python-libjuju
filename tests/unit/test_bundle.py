import unittest

from juju.bundle import ChangeSet
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
