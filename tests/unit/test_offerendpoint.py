#
# Test our offer endpoint parser
#

import unittest

from juju import offerendpoints


class TestOfferEndpoint(unittest.TestCase):

    def test_parse(self):
        _ = offerendpoints.parse
        result = offerendpoints.OfferEndpoints

        cases = [(_("mysql:db"), result("mysql", ["db"])),
                 (_("model/fred.mysql:db"), result("mysql", ["db"], "model", "model/fred")),
                 (_("mysql:db,log"), result("mysql", ["db", "log"]))]
        for case in cases:
            self.assertEqual(case[0], case[1])


class TestOfferURL(unittest.TestCase):

    def test_parse(self):
        _ = offerendpoints.parse_url
        result = offerendpoints.OfferURL

        cases = [(_("controller:user/modelname.applicationname"), result(source="controller", user="user", model="modelname", application="applicationname")),
                 (_("controller:user/modelname.applicationname:rel"), result(source="controller", user="user", model="modelname", application="applicationname:rel")),
                 (_("modelname.applicationname"), result(model="modelname", application="applicationname")),
                 (_("modelname.applicationname:rel"), result(model="modelname", application="applicationname:rel")),
                 (_("/modelname.applicationname"), result(model="modelname", application="applicationname")),
                 (_("/modelname.applicationname:rel"), result(model="modelname", application="applicationname:rel")),
                 (_("user/modelname.applicationname"), result(user="user", model="modelname", application="applicationname")),
                 (_("user/modelname.applicationname:rel"), result(user="user", model="modelname", application="applicationname:rel")),
                 ]
        for case in cases:
            self.assertEqual(case[0], case[1])

    def test_parse_failures(self):
        _ = offerendpoints.parse_url

        cases = [(lambda: _("controller:modelname"), "application offer URL is missing application"),
                 (lambda: _("controller:user/modelname"), "application offer URL is missing application"),
                 (lambda: _("modelname"), "application offer URL is missing application"),
                 (lambda: _("/user/modelname"), "application offer URL is missing application"),
                 (lambda: _("modelname.applicationname@bad"), "application name application@bad not valid"),
                 (lambda: _("user[bad/model.application"), "user name user[bad not valid"),
                 (lambda: _("user/[badmodel.application"), "model name [badmodel not valid"),
                 ]
        for case in cases:
            try:
                case[0]()
            except offerendpoints.ParseError as e:
                self.assertEqual(e.message, case[1])
            except Exception:
                raise

    def test_maybe_parse_source(self):
        _ = offerendpoints.maybe_parse_source

        cases = [(_("name"), ("", "name")),
                 (_("name:app"), ("", "name:app")),
                 (_("name:app:rel"), ("name", "app:rel")),
                 (_("name:app:rel:other"), ("name", "app:rel:other")),
                 ]
        for case in cases:
            self.assertEqual(case[0], case[1])
