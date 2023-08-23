# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import unittest
from juju.client.proxy.kubernetes.proxy import KubernetesProxy


class TestKubernetesProxy(unittest.TestCase):
    def test_remote_port_error(self):
        self.assertRaises(
            ValueError,
            KubernetesProxy,
            api_host="https://localhost:1234",
            namespace="controller",
            remote_port="not-a-integer-port",
            service="service",
            service_account_token="==AA",
        )
