import asyncio
import unittest
import subprocess

import pytest

from juju.client.connection import Connection


def is_bootstrapped():
    result = subprocess.run(['juju', 'switch'], stdout=subprocess.PIPE)
    print(result.stdout)
    return (
        result.returncode == 0 and
        len(result.stdout.decode().strip()) > 0)

bootstrapped = pytest.mark.skipif(
    not is_bootstrapped(),
    reason='bootstrapped Juju environment required')


@bootstrapped
class FunctionalConnectionTest(unittest.TestCase):
    def test_connect_current(self):
        loop = asyncio.get_event_loop()
        conn = loop.run_until_complete(
            Connection.connect_current())

        self.assertIsInstance(conn, Connection)
