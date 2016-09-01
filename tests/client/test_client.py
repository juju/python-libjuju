import asyncio
import unittest

from juju.client.connection import Connection
from juju.client import client

from ..base import bootstrapped


@bootstrapped
class UserManagerTest(unittest.TestCase):
    def test_user_info(self):
        loop = asyncio.get_event_loop()
        conn = loop.run_until_complete(
            Connection.connect_current())
        conn = loop.run_until_complete(
            conn.controller())

        um = client.UserManagerFacade()
        um.connect(conn)
        result = loop.run_until_complete(
            um.UserInfo([client.Entity('user-admin')], True))

        self.assertIsInstance(result, client.UserInfoResults)
        for r in result.results:
            self.assertIsInstance(r, client.UserInfoResult)
