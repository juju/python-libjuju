#
# Test our placement helper
#

import unittest

from juju.utils import generate_user_controller_access_token


class TestRegistrationString(unittest.TestCase):
    def test_generate_user_controller_access_token(self):
        controller_name = "localhost-localhost"
        endpoints = ["192.168.1.1:17070", "192.168.1.2:17070", "192.168.1.3:17070"]
        username = "test-01234"
        secret_key = "paNZrqOw51ONk1kTER6rkm4hdPcg5VgC/dzXYxtUZaM="
        reg_string = generate_user_controller_access_token(username, endpoints, secret_key, controller_name)
        assert reg_string == b"MH4TCnRlc3QtMDEyMzQwORMRMTkyLjE2OC4xLjE6MTcwNzATETE5Mi4xNjguMS4yOjE3MDcwExExOTIuMTY4" \
                             b"LjEuMzoxNzA3MAQgpaNZrqOw51ONk1kTER6rkm4hdPcg5VgC_dzXYxtUZaMTE2xvY2FsaG9zdC1sb2NhbGhvc3QA"
