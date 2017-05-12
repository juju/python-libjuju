import base64
import io
import json
import logging
import os
import random
import shlex
import ssl
import string
import subprocess
import websockets
from concurrent.futures import CancelledError
from http.client import HTTPSConnection
from pathlib import Path

import asyncio
import yaml

from juju import tag, utils
from juju.client import client
from juju.errors import JujuError, JujuAPIError, JujuConnectionError
from juju.utils import IdQueue

log = logging.getLogger("websocket")


class Monitor:
    """
    Monitor helper class for our Connection class.

    Contains a reference to an instantiated Connection, along with a
    reference to the Connection.receiver Future. Upon inspecttion of
    these objects, this class determines whether the connection is in
    an 'error', 'connected' or 'disconnected' state.

    Use this class to stay up to date on the health of a connection,
    and take appropriate action if the connection errors out due to
    network issues or other unexpected circumstances.

    """
    ERROR = 'error'
    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'
    UNKNOWN = 'unknown'

    def __init__(self, connection):
        self.connection = connection
        self.close_called = asyncio.Event(loop=self.connection.loop)
        self.receiver_stopped = asyncio.Event(loop=self.connection.loop)
        self.pinger_stopped = asyncio.Event(loop=self.connection.loop)
        self.receiver_stopped.set()
        self.pinger_stopped.set()

    @property
    def status(self):
        """
        Determine the status of the connection and receiver, and return
        ERROR, CONNECTED, or DISCONNECTED as appropriate.

        For simplicity, we only consider ourselves to be connected
        after the Connection class has setup a receiver task. This
        only happens after the websocket is open, and the connection
        isn't usable until that receiver has been started.

        """

        # DISCONNECTED: connection not yet open
        if not self.connection.ws:
            return self.DISCONNECTED
        if self.receiver_stopped.is_set():
            return self.DISCONNECTED

        # ERROR: Connection closed (or errored), but we didn't call
        # connection.close
        if not self.close_called.is_set() and self.receiver_stopped.is_set():
            return self.ERROR
        if not self.close_called.is_set() and not self.connection.ws.open:
            # The check for self.receiver_stopped existing above guards
            # against the case where we're not open because we simply
            # haven't setup the connection yet.
            return self.ERROR

        # DISCONNECTED: cleanly disconnected.
        if self.close_called.is_set() and not self.connection.ws.open:
            return self.DISCONNECTED

        # CONNECTED: everything is fine!
        if self.connection.ws.open:
            return self.CONNECTED

        # UNKNOWN: We should never hit this state -- if we do,
        # something went wrong with the logic above, and we do not
        # know what state the connection is in.
        return self.UNKNOWN


class Connection:
    """
    Usage::

        # Connect to an arbitrary api server
        client = await Connection.connect(
            api_endpoint, model_uuid, username, password, cacert)

        # Connect using a controller/model name
        client = await Connection.connect_model('local.local:default')

        # Connect to the currently active model
        client = await Connection.connect_current()

    Note: Any connection method or constructor can accept an optional `loop`
    argument to override the default event loop from `asyncio.get_event_loop`.
    """
    def __init__(
            self, endpoint, uuid, username, password, cacert=None,
            macaroons=None, loop=None):
        self.endpoint = endpoint
        self.uuid = uuid
        if macaroons:
            self.macaroons = macaroons
            self.username = ''
            self.password = ''
        else:
            self.macaroons = []
            self.username = username
            self.password = password
        self.cacert = cacert
        self.loop = loop or asyncio.get_event_loop()

        self.__request_id__ = 0
        self.addr = None
        self.ws = None
        self.facades = {}
        self.messages = IdQueue(loop=self.loop)
        self.monitor = Monitor(connection=self)

    @property
    def is_open(self):
        if self.ws:
            return self.ws.open
        return False

    def _get_ssl(self, cert=None):
        return ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH, cadata=cert)

    async def open(self):
        if self.uuid:
            url = "wss://{}/model/{}/api".format(self.endpoint, self.uuid)
        else:
            url = "wss://{}/api".format(self.endpoint)

        kw = dict()
        kw['ssl'] = self._get_ssl(self.cacert)
        kw['loop'] = self.loop
        self.addr = url
        self.ws = await websockets.connect(url, **kw)
        self.loop.create_task(self.receiver())
        self.monitor.receiver_stopped.clear()
        log.info("Driver connected to juju %s", url)
        self.monitor.close_called.clear()
        return self

    async def close(self):
        if not self.is_open:
            return
        self.monitor.close_called.set()
        await self.monitor.pinger_stopped.wait()
        await self.monitor.receiver_stopped.wait()
        await self.ws.close()

    async def recv(self, request_id):
        if not self.is_open:
            raise websockets.exceptions.ConnectionClosed(0, 'websocket closed')
        return await self.messages.get(request_id)

    async def receiver(self):
        try:
            while self.is_open:
                result = await utils.run_with_interrupt(
                    self.ws.recv(),
                    self.monitor.close_called,
                    loop=self.loop)
                if self.monitor.close_called.is_set():
                    break
                if result is not None:
                    result = json.loads(result)
                    await self.messages.put(result['request-id'], result)
        except CancelledError:
            pass
        except Exception as e:
            await self.messages.put_all(e)
            if isinstance(e, websockets.ConnectionClosed):
                # ConnectionClosed is not really exceptional for us,
                # but it may be for any pending message listeners
                return
            log.exception("Error in receiver")
            raise
        finally:
            self.monitor.receiver_stopped.set()

    async def pinger(self):
        '''
        A Controller can time us out if we are silent for too long. This
        is especially true in JaaS, which has a fairly strict timeout.

        To prevent timing out, we send a ping every ten seconds.

        '''
        async def _do_ping():
            try:
                await pinger_facade.Ping()
                await asyncio.sleep(10, loop=self.loop)
            except CancelledError:
                pass

        pinger_facade = client.PingerFacade.from_connection(self)
        try:
            while self.is_open:
                await utils.run_with_interrupt(
                    _do_ping(),
                    self.monitor.close_called,
                    loop=self.loop)
                if self.monitor.close_called.is_set():
                    break
        finally:
            self.monitor.pinger_stopped.set()

    async def rpc(self, msg, encoder=None):
        self.__request_id__ += 1
        msg['request-id'] = self.__request_id__
        if'params' not in msg:
            msg['params'] = {}
        if "version" not in msg:
            msg['version'] = self.facades[msg['type']]
        outgoing = json.dumps(msg, indent=2, cls=encoder)
        await self.ws.send(outgoing)
        result = await self.recv(msg['request-id'])

        if not result:
            return result

        if 'error' in result:
            # API Error Response
            raise JujuAPIError(result)

        if 'response' not in result:
            # This may never happen
            return result

        if 'results' in result['response']:
            # Check for errors in a result list.
            errors = []
            for res in result['response']['results']:
                if res.get('error', {}).get('message'):
                    errors.append(res['error']['message'])
            if errors:
                raise JujuError(errors)

        elif result['response'].get('error', {}).get('message'):
            raise JujuError(result['response']['error']['message'])

        return result

    def http_headers(self):
        """Return dictionary of http headers necessary for making an http
        connection to the endpoint of this Connection.

        :return: Dictionary of headers

        """
        if not self.username:
            return {}

        creds = u'{}:{}'.format(
            tag.user(self.username),
            self.password or ''
        )
        token = base64.b64encode(creds.encode())
        return {
            'Authorization': 'Basic {}'.format(token.decode())
        }

    def https_connection(self):
        """Return an https connection to this Connection's endpoint.

        Returns a 3-tuple containing::

            1. The :class:`HTTPSConnection` instance
            2. Dictionary of auth headers to be used with the connection
            3. The root url path (str) to be used for requests.

        """
        endpoint = self.endpoint
        host, remainder = endpoint.split(':', 1)
        port = remainder
        if '/' in remainder:
            port, _ = remainder.split('/', 1)

        conn = HTTPSConnection(
            host, int(port),
            context=self._get_ssl(self.cacert),
        )

        path = (
            "/model/{}".format(self.uuid)
            if self.uuid else ""
        )
        return conn, self.http_headers(), path

    async def clone(self):
        """Return a new Connection, connected to the same websocket endpoint
        as this one.

        """
        return await Connection.connect(
            self.endpoint,
            self.uuid,
            self.username,
            self.password,
            self.cacert,
            self.macaroons,
            self.loop,
        )

    async def controller(self):
        """Return a Connection to the controller at self.endpoint

        """
        return await Connection.connect(
            self.endpoint,
            None,
            self.username,
            self.password,
            self.cacert,
            self.macaroons,
            self.loop,
        )

    async def _try_endpoint(self, endpoint, cacert):
        success = False
        result = None
        new_endpoints = []

        self.endpoint = endpoint
        self.cacert = cacert
        await self.open()
        try:
            result = await self.login()
            if 'discharge-required-error' in result['response']:
                log.info('Macaroon discharge required, disconnecting')
            else:
                # successful login!
                log.info('Authenticated')
                success = True
        except JujuAPIError as e:
            if e.error_code != 'redirection required':
                raise
            log.info('Controller requested redirect')
            redirect_info = await self.redirect_info()
            redir_cacert = redirect_info['ca-cert']
            new_endpoints = [
                ("{value}:{port}".format(**s), redir_cacert)
                for servers in redirect_info['servers']
                for s in servers if s["scope"] == 'public'
            ]
        finally:
            if not success:
                await self.close()
        return success, result, new_endpoints

    @classmethod
    async def connect(
            cls, endpoint, uuid, username, password, cacert=None,
            macaroons=None, loop=None):
        """Connect to the websocket.

        If uuid is None, the connection will be to the controller. Otherwise it
        will be to the model.

        """
        client = cls(endpoint, uuid, username, password, cacert, macaroons,
                     loop)
        endpoints = [(endpoint, cacert)]
        while endpoints:
            _endpoint, _cacert = endpoints.pop(0)
            success, result, new_endpoints = await client._try_endpoint(
                _endpoint, _cacert)
            if success:
                break
            endpoints.extend(new_endpoints)
        else:
            # ran out of endpoints without a successful login
            raise Exception("Couldn't authenticate to {}".format(endpoint))

        response = result['response']
        client.info = response.copy()
        client.build_facades(response.get('facades', {}))
        client.loop.create_task(client.pinger())
        client.monitor.pinger_stopped.clear()

        return client

    @classmethod
    async def connect_current(cls, loop=None):
        """Connect to the currently active model.

        """
        jujudata = JujuData()

        controller_name = jujudata.current_controller()
        if not controller_name:
            raise JujuConnectionError('No current controller')

        model_name = jujudata.current_model()

        return await cls.connect_model(
            '{}:{}'.format(controller_name, model_name), loop)

    @classmethod
    async def connect_current_controller(cls, loop=None):
        """Connect to the currently active controller.

        """
        jujudata = JujuData()
        controller_name = jujudata.current_controller()
        if not controller_name:
            raise JujuConnectionError('No current controller')

        return await cls.connect_controller(controller_name, loop)

    @classmethod
    async def connect_controller(cls, controller_name, loop=None):
        """Connect to a controller by name.

        """
        jujudata = JujuData()
        controller = jujudata.controllers()[controller_name]
        endpoint = controller['api-endpoints'][0]
        cacert = controller.get('ca-cert')
        accounts = jujudata.accounts()[controller_name]
        username = accounts['user']
        password = accounts.get('password')
        macaroons = get_macaroons(controller_name) if not password else None

        return await cls.connect(
            endpoint, None, username, password, cacert, macaroons, loop)

    @classmethod
    async def connect_model(cls, model, loop=None):
        """Connect to a model by name.

        :param str model: [<controller>:]<model>

        """
        jujudata = JujuData()

        if ':' in model:
            # explicit controller given
            controller_name, model_name = model.split(':')
        else:
            # use the current controller if one isn't explicitly given
            controller_name = jujudata.current_controller()
            model_name = model

        accounts = jujudata.accounts()[controller_name]
        username = accounts['user']
        # model name must include a user prefix, so add it if it doesn't
        if '/' not in model_name:
            model_name = '{}/{}'.format(username, model_name)

        controller = jujudata.controllers()[controller_name]
        endpoint = controller['api-endpoints'][0]
        cacert = controller.get('ca-cert')
        password = accounts.get('password')
        models = jujudata.models()[controller_name]
        model_uuid = models['models'][model_name]['uuid']
        macaroons = get_macaroons(controller_name) if not password else None

        return await cls.connect(
            endpoint, model_uuid, username, password, cacert, macaroons, loop)

    def build_facades(self, facades):
        self.facades.clear()
        for facade in facades:
            self.facades[facade['name']] = facade['versions'][-1]

    async def login(self):
        username = self.username
        if username and not username.startswith('user-'):
            username = 'user-{}'.format(username)

        result = await self.rpc({
            "type": "Admin",
            "request": "Login",
            "version": 3,
            "params": {
                "auth-tag": username,
                "credentials": self.password,
                "nonce": "".join(random.sample(string.printable, 12)),
                "macaroons": self.macaroons
            }})
        return result

    async def redirect_info(self):
        try:
            result = await self.rpc({
                "type": "Admin",
                "request": "RedirectInfo",
                "version": 3,
            })
        except JujuAPIError as e:
            if e.message == 'not redirected':
                return None
            raise
        return result['response']


class JujuData:
    def __init__(self):
        self.path = os.environ.get('JUJU_DATA') or '~/.local/share/juju'
        self.path = os.path.abspath(os.path.expanduser(self.path))

    def current_controller(self):
        cmd = shlex.split('juju list-controllers --format yaml')
        output = subprocess.check_output(cmd)
        output = yaml.safe_load(output)
        return output.get('current-controller', '')

    def current_model(self, controller_name=None):
        if not controller_name:
            controller_name = self.current_controller()
        models = self.models()[controller_name]
        if 'current-model' not in models:
            raise JujuError('No current model')
        return models['current-model']

    def controllers(self):
        return self._load_yaml('controllers.yaml', 'controllers')

    def models(self):
        return self._load_yaml('models.yaml', 'controllers')

    def accounts(self):
        return self._load_yaml('accounts.yaml', 'controllers')

    def _load_yaml(self, filename, key):
        filepath = os.path.join(self.path, filename)
        with io.open(filepath, 'rt') as f:
            return yaml.safe_load(f)[key]


def get_macaroons(controller_name=None):
    """Decode and return macaroons from default ~/.go-cookies

    """
    cookie_files = []
    if controller_name:
        cookie_files.append('~/.local/share/juju/cookies/{}.json'.format(
            controller_name))
    cookie_files.append('~/.go-cookies')
    for cookie_file in cookie_files:
        cookie_file = Path(cookie_file).expanduser()
        if cookie_file.exists():
            try:
                cookies = json.loads(cookie_file.read_text())
                break
            except (OSError, ValueError):
                log.warn("Couldn't load macaroons from %s", cookie_file)
                return []
    else:
        log.warn("Couldn't load macaroons from %s", ' or '.join(cookie_files))
        return []

    base64_macaroons = [
        c['Value'] for c in cookies
        if c['Name'].startswith('macaroon-') and c['Value']
    ]

    return [
        json.loads(base64.b64decode(value).decode('utf-8'))
        for value in base64_macaroons
    ]
