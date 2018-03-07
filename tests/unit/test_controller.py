import asynctest
import mock
from pathlib import Path
from tempfile import NamedTemporaryFile

from juju.controller import Controller
from juju.client import client

from .. import base


class TestControllerConnect(asynctest.TestCase):
    @asynctest.patch('juju.client.connector.Connector.connect_controller')
    async def test_no_args(self, mock_connect_controller):
        c = Controller()
        await c.connect()
        mock_connect_controller.assert_called_once_with(None)

    @asynctest.patch('juju.client.connector.Connector.connect_controller')
    async def test_with_controller_name(self, mock_connect_controller):
        c = Controller()
        await c.connect(controller_name='foo')
        mock_connect_controller.assert_called_once_with('foo')

    @asynctest.patch('juju.client.connector.Connector.connect')
    async def test_with_endpoint_and_no_auth(self, mock_connect):
        c = Controller()
        with self.assertRaises(TypeError):
            await c.connect(endpoint='0.1.2.3:4566')
        self.assertEqual(mock_connect.call_count, 0)

    @asynctest.patch('juju.client.connector.Connector.connect')
    async def test_with_endpoint_and_userpass(self, mock_connect):
        c = Controller()
        with self.assertRaises(TypeError):
            await c.connect(endpoint='0.1.2.3:4566', username='dummy')
        await c.connect(endpoint='0.1.2.3:4566',
                        username='user',
                        password='pass')
        mock_connect.assert_called_once_with(endpoint='0.1.2.3:4566',
                                             username='user',
                                             password='pass')

    @asynctest.patch('juju.client.connector.Connector.connect')
    async def test_with_endpoint_and_bakery_client(self, mock_connect):
        c = Controller()
        await c.connect(endpoint='0.1.2.3:4566', bakery_client='bakery')
        mock_connect.assert_called_once_with(endpoint='0.1.2.3:4566',
                                             bakery_client='bakery')

    @asynctest.patch('juju.client.connector.Connector.connect')
    async def test_with_endpoint_and_macaroons(self, mock_connect):
        c = Controller()
        await c.connect(endpoint='0.1.2.3:4566',
                        macaroons=['macaroon'])
        mock_connect.assert_called_with(endpoint='0.1.2.3:4566',
                                        macaroons=['macaroon'])
        await c.connect(endpoint='0.1.2.3:4566',
                        bakery_client='bakery',
                        macaroons=['macaroon'])
        mock_connect.assert_called_with(endpoint='0.1.2.3:4566',
                                        bakery_client='bakery',
                                        macaroons=['macaroon'])

    @asynctest.patch('juju.client.connector.Connector.connect_controller')
    @asynctest.patch('juju.client.connector.Connector.connect')
    async def test_with_posargs(self, mock_connect, mock_connect_controller):
        c = Controller()
        await c.connect('foo')
        mock_connect_controller.assert_called_once_with('foo')
        with self.assertRaises(TypeError):
            await c.connect('endpoint', 'user')
        await c.connect('endpoint', 'user', 'pass')
        mock_connect.assert_called_once_with(endpoint='endpoint',
                                             username='user',
                                             password='pass')
        await c.connect('endpoint', 'user', 'pass', 'cacert', 'bakery',
                        'macaroons', 'loop', 'max_frame_size')
        mock_connect.assert_called_with(endpoint='endpoint',
                                        username='user',
                                        password='pass',
                                        cacert='cacert',
                                        bakery_client='bakery',
                                        macaroons='macaroons',
                                        loop='loop',
                                        max_frame_size='max_frame_size')

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
