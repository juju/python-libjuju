# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import unittest

from juju.client.proxy.factory import proxy_from_config
from juju.client.proxy.kubernetes.proxy import KubernetesProxy


class TestJujuDataFactory(unittest.TestCase):

    def test_proxy_from_config_unknown_type(self):
        """
        Test that a unknown proxy type results in a UnknownProxyTypeError
        exception
        """
        self.assertRaises(ValueError, proxy_from_config, {
            "config": {},
            "type": "does-not-exists",
        })

    def test_proxy_from_config_missing_type(self):
        """
        Test that a nil proxy type returns None
        """
        self.assertIsNone(proxy_from_config({
            "config": {},
        }))

    def test_proxy_from_config_non_arg(self):
        """
        Tests that providing an empty proxy config results in a None proxy
        """
        self.assertIsNone(proxy_from_config(None))

    def test_proxy_from_config_kubernetes(self):
        """
        Tests that a Kubernetes proxy is correctly created from config
        """
        proxy = proxy_from_config({
            "type": "kubernetes-port-forward",
            "config": {
                "api-host": "https://localhost:8456",
                "namespace": "controller-python-test",
                "remote-port": "1234",
                "service": "controller",
                "service-account-token": "==AA",
                "ca-cert": "==AA",
            },
        })

        self.assertIs(type(proxy), KubernetesProxy)
