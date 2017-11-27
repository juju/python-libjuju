import asyncio
import base64
import json
import logging
import ssl
import urllib.request
import weakref
from concurrent.futures import CancelledError
from http.client import HTTPSConnection

import macaroonbakery.httpbakery as httpbakery
import websockets
from juju import utils
from juju.client import client
from juju.errors import JujuAPIError, JujuError
from juju.utils import IdQueue

log = logging.getLogger("websocket")


class Monitor:
    """
    Monitor helper class for our Connection class.

    Contains a reference to an instantiated Connection, along with a
    reference to the Connection.receiver Future. Upon inspection of
    these objects, this class determines whether the connection is in
    an 'error', 'connected' or 'disconnected' state.

    Use this class to stay up to date on the health of a connection,
    and take appropriate action if the connection errors out due to
    network issues or other unexpected circumstances.

    """
    ERROR = 'error'
    CONNECTED = 'connected'
    DISCONNECTING = 'disconnecting'
    DISCONNECTED = 'disconnected'

    def __init__(self, connection):
        self.connection = weakref.ref(connection)
        self.reconnecting = asyncio.Lock(loop=connection.loop)
        self.close_called = asyncio.Event(loop=connection.loop)

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
        connection = self.connection()

        # the connection instance was destroyed but someone kept
        # a separate reference to the monitor for some reason
        if not connection:
            return self.DISCONNECTED

        # connection cleanly disconnected or not yet opened
        if not connection.ws:
            return self.DISCONNECTED

        # close called but not yet complete
        if self.close_called.is_set():
            return self.DISCONNECTING

        # connection closed uncleanly (we didn't call connection.close)
        if connection._receiver_task.stopped.is_set() or not connection.ws.open:
            return self.ERROR

        # everything is fine!
        return self.CONNECTED


class Connection:
    """
    Usage::

        # Connect to an arbitrary api server
        client = await Connection.connect(
            api_endpoint, model_uuid, username, password, cacert)

    Note: Any connection method or constructor can accept an optional `loop`
    argument to override the default event loop from `asyncio.get_event_loop`.
    """

    MAX_FRAME_SIZE = 2**22
    "Maximum size for a single frame.  Defaults to 4MB."

    @classmethod
    async def connect(
            cls,
            endpoint,
            uuid=None,
            username=None,
            password=None,
            cacert=None,
            bakery_client=None,
            loop=None,
            max_frame_size=None,
    ):
        """Connect to the websocket.

        If uuid is None, the connection will be to the controller. Otherwise it
        will be to the model.
        :param str endpoint The hostname:port of the controller to connect to.
        :param str uuid The model UUID to connect to (None for a
            controller-only connection).
        :param str username The username for controller-local users (or None
            to use macaroon-based login.)
        :param str password The password for controller-local users.
        :param str cacert The CA certificate of the controller (PEM formatted).
        :param httpbakery.Client bakery_client The macaroon bakery client to
            to use when performing macaroon-based login. Macaroon tokens
            acquired when logging will be saved to bakery_client.cookies.
            If this is None, a default bakery_client will be used.
        :param loop asyncio.BaseEventLoop The event loop to use for async
            operations.
        :param max_frame_size The maximum websocket frame size to allow.
        """
        self = cls()
        self.uuid = uuid
        if bakery_client is None:
            bakery_client = httpbakery.Client()
        self.bakery_client = bakery_client
        self.usertag = username
        if username is not None and not username.startswith('user-'):
            # TODO this doesn't seem quite right, as 'user-foo' is
            # actually a valid username (its tag would be user-user-foo),
            # but don't break the existing API.
            self.usertag = 'user-' + username
        self.password = password
        self.loop = loop or asyncio.get_event_loop()

        self.__request_id__ = 0

        # The following instance variables are initialized by the
        # _connect_with_redirect method, but create them here
        # as a reminder that they will exist.
        self.addr = None
        self.ws = None
        self.endpoint = None
        self.cacert = None
        self.info = None

        # Create that _Task objects but don't start the tasks yet.
        self._pinger_task = _Task(self._pinger, self.loop)
        self._receiver_task = _Task(self._receiver, self.loop)

        self.facades = {}
        self.messages = IdQueue(loop=self.loop)
        self.monitor = Monitor(connection=self)
        if max_frame_size is None:
            max_frame_size = self.MAX_FRAME_SIZE
        self.max_frame_size = max_frame_size
        await self._connect_with_redirect([(endpoint, cacert)])
        return self

    @property
    def username(self):
        if not self.usertag:
            return None
        return self.usertag[len('user-'):]

    @property
    def is_open(self):
        return self.monitor.status == Monitor.CONNECTED

    def _get_ssl(self, cert=None):
        return ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH, cadata=cert)

    async def _open(self, endpoint, cacert):
        if self.uuid:
            url = "wss://{}/model/{}/api".format(endpoint, self.uuid)
        else:
            url = "wss://{}/api".format(endpoint)

        return (await websockets.connect(
            url,
            ssl=self._get_ssl(cacert),
            loop=self.loop,
            max_size=self.max_frame_size,
        ), url)

    async def close(self):
        if not self.ws:
            return
        self.monitor.close_called.set()
        await self._pinger_task.stopped.wait()
        await self._receiver_task.stopped.wait()
        await self.ws.close()
        self.ws = None

    async def _recv(self, request_id):
        if not self.is_open:
            raise websockets.exceptions.ConnectionClosed(0, 'websocket closed')
        return await self.messages.get(request_id)

    async def _receiver(self):
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
        except websockets.ConnectionClosed as e:
            log.warning('Receiver: Connection closed, reconnecting')
            await self.messages.put_all(e)
            # the reconnect has to be done as a task because the receiver will
            # be cancelled by the reconnect and we don't want the reconnect
            # to be aborted half-way through
            self.loop.create_task(self.reconnect())
            return
        except Exception as e:
            log.exception("Error in receiver")
            # make pending listeners aware of the error
            await self.messages.put_all(e)
            raise

    async def _pinger(self):
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
        while True:
            await utils.run_with_interrupt(
                _do_ping(),
                self.monitor.close_called,
                loop=self.loop)
            if self.monitor.close_called.is_set():
                break

    async def rpc(self, msg, encoder=None):
        '''Make an RPC to the API. The message is encoded as JSON
        using the given encoder if any.
        :param msg: Parameters for the call (will be encoded as JSON).
        :param encoder: Encoder to be used when encoding the message.
        :return: The result of the call.
        :raises JujuAPIError: When there's an error returned.
        :raises JujuError:
        '''
        self.__request_id__ += 1
        msg['request-id'] = self.__request_id__
        if'params' not in msg:
            msg['params'] = {}
        if "version" not in msg:
            msg['version'] = self.facades[msg['type']]
        outgoing = json.dumps(msg, indent=2, cls=encoder)
        log.debug('connection {} -> {}'.format(id(self), outgoing))
        for attempt in range(3):
            try:
                await self.ws.send(outgoing)
                break
            except websockets.ConnectionClosed:
                if attempt == 2:
                    raise
                log.warning('RPC: Connection closed, reconnecting')
                # the reconnect has to be done in a separate task because,
                # if it is triggered by the pinger, then this RPC call will
                # be cancelled when the pinger is cancelled by the reconnect,
                # and we don't want the reconnect to be aborted halfway through
                await asyncio.wait([self.reconnect()], loop=self.loop)
        result = await self._recv(msg['request-id'])
        log.debug('connection {} <- {}'.format(id(self), result))

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
            # TODO This loses the results that might have succeeded.
            # Perhaps JujuError should return all the results including
            # errors, or perhaps a keyword parameter to the rpc method
            # could be added to trigger this behaviour.
            errors = []
            for res in result['response']['results']:
                if res.get('error', {}).get('message'):
                    errors.append(res['error']['message'])
            if errors:
                raise JujuError(errors)

        elif result['response'].get('error', {}).get('message'):
            raise JujuError(result['response']['error']['message'])

        return result

    def _http_headers(self):
        """Return dictionary of http headers necessary for making an http
        connection to the endpoint of this Connection.

        :return: Dictionary of headers

        """
        if not self.usertag:
            return {}

        creds = u'{}:{}'.format(
            self.usertag,
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
        return conn, self._http_headers(), path

    async def clone(self):
        """Return a new Connection, connected to the same websocket endpoint
        as this one.

        """
        endpoint, kwargs = self.connect_params()

        return await Connection.connect(endpoint, **kwargs)

    def connect_params(self):
        """Return a tuple of parameters suitable for passing to Connection.connect that
        can be used to make a new connection to the same controller (and model
        if specified. The first element in the returned tuple holds the endpoint argument; the other
        holds a dict of the keyword args.
        """
        # TODO if the connect method took all keyword arguments then this could
        # be simpler and just return a dict rather than a tuple.
        return (
            self.endpoint, {
                'uuid': self.uuid,
                'username': self.username,
                'password': self.password,
                'cacert': self.cacert,
                'bakery_client': self.bakery_client,
                'loop': self.loop,
                'max_frame_size': self.max_frame_size,
            }
        )

    async def controller(self):
        """Return a Connection to the controller at self.endpoint
        """
        return await Connection.connect(
            self.endpoint,
            username=self.username,
            password=self.password,
            cacert=self.cacert,
            bakery_client=self.bakery_client,
            loop=self.loop,
            max_frame_size=self.max_frame_size,
        )

    async def reconnect(self):
        """ Force a reconnection.
        """
        monitor = self.monitor
        if monitor.reconnecting.locked() or monitor.close_called.is_set():
            return
        async with monitor.reconnecting:
            await self.close()
            await self._connect_with_login([(self.endpoint, self.cacert)])

    async def _connect(self, endpoints):
        if len(endpoints) == 0:
            raise Exception('no endpoints to connect to')
        first_exception = None
        # TODO try connecting concurrently.
        for endpoint, cacert in endpoints:
            try:
                self.ws, self.addr = await self._open(endpoint, cacert)
                self.endpoint = endpoint
                self.cacert = cacert
                self._receiver_task.start()
                log.info("Driver connected to juju %s", self.addr)
                self.monitor.close_called.clear()
                return
            except Exception as e:
                if first_exception is None:
                    first_exception = e
        raise first_exception

    async def _connect_with_login(self, endpoints):
        """Connect to the websocket.

        If uuid is None, the connection will be to the controller. Otherwise it
        will be to the model.
        :return: The login response JSON object.
        """
        success = False
        try:
            await self._connect(endpoints)
           # It's possible that we may get several discharge-required errors,
            # corresponding to different levels of authentication, so retry
            # a few times.
            for i in range(0, 4):
                result = await self.login()
                macaroonJSON = result.get('discharge-required')
                if macaroonJSON is None:
                    self.info = result['response']
                    success = True
                    return result
                # TODO implement macaroon authentication
                raise NotImplementedError('macaroon authentication not implemented yet')
        finally:
            if not success:
                await self.close()

    async def _connect_with_redirect(self, endpoints):
        try:
            login_result = await self._connect_with_login(endpoints)
        except JujuAPIError as e:
            if e.error_code != 'redirection required':
                raise
            log.info('Controller requested redirect')
            redirect_info = await self.redirect_info()
            redir_cacert = redirect_info['ca-cert']
            new_endpoints = [
                ('{value}:{port}'.format(**s), redir_cacert)
                for servers in redirect_info['servers']
                for s in servers if s['scope'] == 'public'
            ]
            login_result = await self._connect_with_login(new_endpoints)
        response = login_result['response']
        self._build_facades(response.get('facades', {}))
        self._pinger_task.start()

    def _build_facades(self, facades):
        self.facades.clear()
        for facade in facades:
            self.facades[facade['name']] = facade['versions'][-1]

    async def login(self):
        params = {}
        if self.usertag:
            params['auth-tag'] = self.usertag
            params['credentials'] = self.password
        else:
            params['macaroons'] = _macaroons_for_domain(self.bakery_client.cookies, self.endpoint)

        return await self.rpc({
            "type": "Admin",
            "request": "Login",
            "version": 3,
            "params": params,
        })

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


class _Task:
    def __init__(self, task, loop):
        self.stopped = asyncio.Event(loop=loop)
        self.stopped.set()
        self.task = task
        self.loop = loop

    def start(self):
        async def run():
            try:
                return await(self.task())
            finally:
                self.stopped.set()
        self.stopped.clear()
        self.loop.create_task(run())


def _macaroons_for_domain(cookies, domain):
    '''Return any macaroons from the given cookie jar that
    apply to the given domain name.'''
    req = urllib.request.Request('https://' + domain + '/')
    cookies.add_cookie_header(req)
    return httpbakery.extract_macaroons(req.headers)
