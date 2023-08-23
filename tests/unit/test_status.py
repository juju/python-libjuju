# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import unittest


from juju.status import derive_status
from random import sample


class TestStatus(unittest.TestCase):
    def test_derive_status_with_empty_list(self):
        result = derive_status([])
        self.assertEqual(result, 'unknown')

    def test_derive_status_with_unknown(self):
        result = derive_status(['unknown'])
        self.assertEqual(result, 'unknown')

    def test_derive_status_with_invalid(self):
        result = derive_status(['boom'])
        self.assertEqual(result, 'unknown')

    def test_derive_status_with_highest_value(self):
        result = derive_status(sample(['error', 'active', 'terminated'], 3))
        self.assertEqual(result, 'error')
