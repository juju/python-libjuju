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

import yaml

from juju.errors import JujuAPIError

log = logging.getLogger("websocket")


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

    """
    def __init__(
            self, endpoint, uuid, username, password, cacert=None,
            macaroons=None):
        self.endpoint = endpoint
        self.uuid = uuid
        self.username = username
        self.password = password
        self.macaroons = macaroons
        self.cacert = cacert

        self.__request_id__ = 0
        self.addr = None
        self.ws = None
        self.facades = {}

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
        self.addr = url
        self.ws = await websockets.connect(url, **kw)
        log.info("Driver connected to juju %s", url)
        return self

    async def close(self):
        await self.ws.close()

    async def recv(self):
        result = await self.ws.recv()
        if result is not None:
            result = json.loads(result)
        return result

    async def rpc(self, msg, encoder=None):
        self.__request_id__ += 1
        msg['request-id'] = self.__request_id__
        if'params' not in msg:
            msg['params'] = {}
        if "version" not in msg:
            msg['version'] = self.facades[msg['type']]
        outgoing = json.dumps(msg, indent=2, cls=encoder)
        await self.ws.send(outgoing)
        result = await self.recv()
        if result and 'error' in result:
            raise JujuAPIError(result)
        return result

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
        )

    @classmethod
    async def connect(
            cls, endpoint, uuid, username, password, cacert=None,
            macaroons=None):
        """Connect to the websocket.

        If uuid is None, the connection will be to the controller. Otherwise it
        will be to the model.

        """
        client = cls(endpoint, uuid, username, password, cacert, macaroons)
        await client.open()

        redirect_info = await client.redirect_info()
        if not redirect_info:
            await client.login(username, password, macaroons)
            return client

        await client.close()
        servers = [
            s for servers in redirect_info['servers']
            for s in servers if s["scope"] == 'public'
        ]
        for server in servers:
            client = cls(
                "{value}:{port}".format(**server), uuid, username,
                password, redirect_info['ca-cert'], macaroons)
            await client.open()
            try:
                result = await client.login(username, password, macaroons)
                if 'discharge-required-error' in result:
                    continue
                return client
            except Exception as e:
                await client.close()
                log.exception(e)

        raise Exception(
            "Couldn't authenticate to %s", endpoint)

    @classmethod
    async def connect_current(cls):
        """Connect to the currently active model.

        """
        jujudata = JujuData()
        controller_name = jujudata.current_controller()
        models = jujudata.models()[controller_name]
        model_name = models['current-model']

        return await cls.connect_model(
            '{}:{}'.format(controller_name, model_name))

    @classmethod
    async def connect_current_controller(cls):
        """Connect to the currently active controller.

        """
        jujudata = JujuData()
        controller_name = jujudata.current_controller()

        return await cls.connect_controller(controller_name)

    @classmethod
    async def connect_controller(cls, controller_name):
        """Connect to a controller by name.

        """
        jujudata = JujuData()
        controller = jujudata.controllers()[controller_name]
        endpoint = controller['api-endpoints'][0]
        cacert = controller.get('ca-cert')
        accounts = jujudata.accounts()[controller_name]
        username = accounts['user']
        password = accounts.get('password')
        macaroons = get_macaroons() if not password else None

        return await cls.connect(
            endpoint, None, username, password, cacert, macaroons)

    @classmethod
    async def connect_model(cls, model):
        """Connect to a model by name.

        :param str model: <controller>:<model>

        """
        controller_name, model_name = model.split(':')

        jujudata = JujuData()
        controller = jujudata.controllers()[controller_name]
        endpoint = controller['api-endpoints'][0]
        cacert = controller.get('ca-cert')
        accounts = jujudata.accounts()[controller_name]
        username = accounts['user']
        password = accounts.get('password')
        models = jujudata.models()[controller_name]
        model_uuid = models['models'][model_name]['uuid']
        macaroons = get_macaroons() if not password else None

        return await cls.connect(
            endpoint, model_uuid, username, password, cacert, macaroons)

    def build_facades(self, info):
        self.facades.clear()
        for facade in info:
            self.facades[facade['name']] = facade['versions'][-1]

    async def login(self, username, password, macaroons=None):
        if macaroons:
            username = ''
            password = ''

        if username and not username.startswith('user-'):
            username = 'user-{}'.format(username)

        result = await self.rpc({
            "type": "Admin",
            "request": "Login",
            "version": 3,
            "params": {
                "auth-tag": username,
                "credentials": password,
                "nonce": "".join(random.sample(string.printable, 12)),
                "macaroons": macaroons or []
            }})
        response = result['response']
        self.build_facades(response.get('facades', {}))
        self.info = response.copy()
        return response

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
        cmd = shlex.split('juju show-controller --format yaml')
        output = subprocess.check_output(cmd)
        output = yaml.safe_load(output)
        return list(output.keys())[0]

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


def get_macaroons():
    """Decode and return macaroons from default ~/.go-cookies

    """
    try:
        cookie_file = os.path.expanduser('~/.go-cookies')
        with open(cookie_file, 'r') as f:
            cookies = json.load(f)
    except (OSError, ValueError) as e:
        log.warn("Couldn't load macaroons from %s", cookie_file)
        return []

    base64_macaroons = [
        c['Value'] for c in cookies
        if c['Name'].startswith('macaroon-') and c['Value']
    ]

    return [
        json.loads(base64.b64decode(value).decode('utf-8'))
        for value in base64_macaroons
    ]
