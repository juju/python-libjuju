import asyncio
import json
import logging
import random
import ssl
import string
import websockets


log = logging.getLogger("websocket")

class Connection:
    """
    Usage:
        client  = await Connection.connect(info)
    """
    def __init__(self):
        self.__requestId__ = 0
        self.addr = None
        self.ws = None

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

    async def rpc(self, msg):
        self.__requestID += 1
        msg['RequestId'] = self.__requestID
        if'Params' not in msg:
            msg['Params'] = {}
        if "Version" not in msg:
            msg['Version'] = self.facades[msg['Type']]
        outgoing = json.dumps(msg, indent=2)
        await self.ws.send(outgoing)
        result = await self.recv()
        log.debug("send %s got %s", msg, result)
        if result and 'Error' in result:
            raise RuntimeError(result)
        return result

    @classmethod
    async def connect(cls, info):
        uuid = info.model_uuid
        controller = info.controller
        details = controller['details']
        endpoint = "wss://{}/model/{}/api".format(
            details['api-endpoints'][0],
            entity.model_uuid)
        client = cls()
        await client.dial(endpoint, details['ca-cert'])
        server_info = await client.login(info)
        client.build_facades(server_info['facades'])
        log.info("Driver connected to juju %s", endpoint)
        return client

    def build_facades(self, info):
        self.facades.clear()
        for facade in info:
            self.facades[facade['Name']] = facade['Versions'][-1]

    async def login(self, info):
        account = info.account
        result = await client.rpc({
            "Type": "Admin",
            "Request": "Login",
            "Version": 3,
            "Params": {
                "auth-tag": "user-{}".format(account['user']),
                "credentials": account['password'],
                "Nonce": "".join(random.sample(string.printable, 12)),
            }})
        return result['Response']


