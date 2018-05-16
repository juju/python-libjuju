import asynctest
import mock
from pathlib import Path
from tempfile import NamedTemporaryFile

from juju.controller import Controller
from juju.client import client

from .. import base


class TestControllerConnect(asynctest.TestCase):
    @asynctest.patch('juju.client.connector.Connector.connect_controller')
    async def test_controller_connect_no_args(self, mock_connect_controller):
        c = Controller()
        await c.connect()
        mock_connect_controller.assert_called_once_with(None)

    @asynctest.patch('juju.client.connector.Connector.connect_controller')
    async def test_controller_connect_with_controller_name(
        self, mock_connect_controller
    ):
        c = Controller()
        await c.connect(controller_name='foo')
        mock_connect_controller.assert_called_once_with('foo')

    @asynctest.patch('juju.client.connector.Connector.connect_controller')
    async def test_controller_connect_with_endpoint_and_uuid(
        self,
        mock_connect_controller,
    ):
        c = Controller()
        with self.assertRaises(ValueError):
            await c.connect(endpoint='0.1.2.3:4566', uuid='some-uuid')
        self.assertEqual(mock_connect_controller.call_count, 0)

    @asynctest.patch('juju.client.connector.Connector.connect')
    async def test_controller_connect_with_endpoint_and_no_uuid(
        self,
        mock_connect,
    ):
        c = Controller()
        await c.connect(endpoint='0.1.2.3:4566')
        mock_connect.assert_called_once_with(endpoint='0.1.2.3:4566')

    @asynctest.patch('juju.client.client.CloudFacade')
    async def test_file_cred(self, mock_cf):
        with NamedTemporaryFile() as tempfile:
            tempfile.close()
            temppath = Path(tempfile.name)
            temppath.write_text('cred-test')
            cred = client.CloudCredential(auth_type='jsonfile',
                                          attrs={'file': tempfile.name})
            jujudata = mock.MagicMock()
            c = Controller(jujudata=jujudata)
            c._connector = base.AsyncMock()
            up_creds = base.AsyncMock()
            mock_cf.from_connection().UpdateCredentials = up_creds
            await c.add_credential(
                name='name',
                credential=cred,
                cloud='cloud',
                owner='owner',
            )
            assert up_creds.called
            new_cred = up_creds.call_args[0][0][0].credential
            assert cred.attrs['file'] == tempfile.name
            assert new_cred.attrs['file'] == 'cred-test'
