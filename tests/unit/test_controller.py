import asynctest


class TestControllerConnect(asynctest.TestCase):
    @asynctest.patch('juju.client.connector.Connector.connect_controller')
    async def test_controller_connect_no_args(self, mock_connect_controller):
        from juju.controller import Controller
        c = Controller()
        await c.connect()
        mock_connect_controller.assert_called_once_with(None)

    @asynctest.patch('juju.client.connector.Connector.connect_controller')
    async def test_controller_connect_with_controller_name(self, mock_connect_controller):
        from juju.controller import Controller
        c = Controller()
        await c.connect(controller_name='foo')
        mock_connect_controller.assert_called_once_with('foo')

    @asynctest.patch('juju.client.connector.Connector.connect_controller')
    async def test_controller_connect_with_endpoint_and_uuid(
        self,
        mock_connect_controller,
    ):
        from juju.controller import Controller
        c = Controller()
        with self.assertRaises(ValueError):
            await c.connect(endpoint='0.1.2.3:4566', uuid='some-uuid')
        self.assertEqual(mock_connect_controller.call_count, 0)

    @asynctest.patch('juju.client.connector.Connector.connect')
    async def test_controller_connect_with_endpoint_and_no_uuid(
        self,
        mock_connect,
    ):
        from juju.controller import Controller
        c = Controller()
        await c.connect(endpoint='0.1.2.3:4566')
        mock_connect.assert_called_once_with(endpoint='0.1.2.3:4566')
