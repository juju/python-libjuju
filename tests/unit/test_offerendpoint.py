#
# Test our offer endpoint parser
#

import unittest

from juju import offerendpoints


class TestOfferEndpoint(unittest.TestCase):

    def test_parse(self):
        _ = offerendpoints.parse
        result = offerendpoints.OfferEndpoints

        cases = [(_("mysql:db"), result("mysql", ["db"])), \
                 (_("model/fred.mysql:db"), result("mysql", ["db"], "model", "model/fred")), \
                 (_("mysql:db,log"), result("mysql", ["db", "log"]))]
        for case in cases:
            self.assertEqual(case[0], case[1])
