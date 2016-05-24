import asyncio
import unittest

from juju.client.connection import Connection
from juju.client.client import UserManager, Entity

from ..base import bootstrapped


@bootstrapped
class UserManagerTest(unittest.TestCase):
    def test_connect_current(self):
        loop = asyncio.get_event_loop()
        conn = loop.run_until_complete(
            Connection.connect_current())

        um = UserManager()
        um.connect(conn)
        result = loop.run_until_complete(
            um.UserInfo([Entity('user-admin')], True))

        assert result
