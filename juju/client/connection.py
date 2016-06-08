import asyncio
import io
import json
import logging
import os
import random
import ssl
import string
import websockets

import yaml

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
    def __init__(self):
        self.__request_id__ = 0
        self.addr = None
        self.ws = None
        self.facades = {}

    def _get_ssl(self, cert):
        return ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH, cadata=cert)

    async def open(self, addr, cert=None):
        kw = dict()
        if cert:
            kw['ssl'] = self._get_ssl(cert)
        self.addr = addr
        self.ws = await websockets.connect(addr, **kw)
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
        msg['RequestId'] = self.__request_id__
        if'Params' not in msg:
            msg['Params'] = {}
        if "Version" not in msg:
            msg['Version'] = self.facades[msg['Type']]
        outgoing = json.dumps(msg, indent=2, cls=encoder)
        await self.ws.send(outgoing)
        result = await self.recv()
        log.debug("send %s got %s", msg, result)
        if result and 'Error' in result:
            raise RuntimeError(result)
        return result

    @classmethod
    async def connect(cls, endpoint, uuid, username, password, cacert=None):
        url = "wss://{}/model/{}/api".format(endpoint, uuid)
        client = cls()
        await client.open(url, cacert)
        server_info = await client.login(username, password)
        client.build_facades(server_info['facades'])
        log.info("Driver connected to juju %s", endpoint)
        return client

    @classmethod
    async def connect_current(cls):
        """Connect to the currently active model.

        """
        jujudata = JujuData()
        controller_name = jujudata.current_controller()
        controller = jujudata.controllers()[controller_name]
        endpoint = controller['api-endpoints'][0]
        cacert = controller.get('ca-cert')
        accounts = jujudata.accounts()[controller_name]
        username = accounts['current-account']
        password = accounts['accounts'][username]['password']
        models = jujudata.models()[controller_name]['accounts'][username]
        model_name = models['current-model']
        model_uuid = models['models'][model_name]['uuid']

        return await cls.connect(
            endpoint, model_uuid, username, password, cacert)

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
        username = accounts['current-account']
        password = accounts['accounts'][username]['password']
        models = jujudata.models()[controller_name]['accounts'][username]
        model_uuid = models['models'][model_name]['uuid']

        return await cls.connect(
            endpoint, model_uuid, username, password, cacert)

    def build_facades(self, info):
        self.facades.clear()
        for facade in info:
            self.facades[facade['Name']] = facade['Versions'][-1]

    async def login(self, username, password):
        if not username.startswith('user-'):
            username = 'user-{}'.format(username)

        result = await self.rpc({
            "Type": "Admin",
            "Request": "Login",
            "Version": 3,
            "Params": {
                "auth-tag": username,
                "credentials": password,
                "Nonce": "".join(random.sample(string.printable, 12)),
            }})
        return result['Response']


class JujuData:
    def __init__(self):
        self.path = os.environ.get('JUJU_DATA') or '~/.local/share/juju'
        self.path = os.path.abspath(os.path.expanduser(self.path))

    def current_controller(self):
        try:
            filepath = os.path.join(self.path, 'current-controller')
            with io.open(filepath, 'rt') as f:
                return f.read().strip()
        except OSError as e:
            log.exception(e)
            return None

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
