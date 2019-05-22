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
import macaroonbakery.bakery as bakery
import websockets
from juju import errors, tag, utils
from juju.client import client
from juju.utils import IdQueue

log = logging.getLogger('juju.client.connection')


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
        stopped = connection._receiver_task.stopped.is_set()
        if stopped or not connection.ws.open:
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
            endpoint=None,
            uuid=None,
            username=None,
            password=None,
            cacert=None,
            bakery_client=None,
            loop=None,
            max_frame_size=None,
            retries=3,
            retry_backoff=10,
    ):
        """Connect to the websocket.

        If uuid is None, the connection will be to the controller. Otherwise it
        will be to the model.

        :param str endpoint: The hostname:port of the controller to connect to.
        :param str uuid: The model UUID to connect to (None for a
            controller-only connection).
        :param str username: The username for controller-local users (or None
            to use macaroon-based login.)
        :param str password: The password for controller-local users.
        :param str cacert: The CA certificate of the controller
            (PEM formatted).
        :param httpbakery.Client bakery_client: The macaroon bakery client to
            to use when performing macaroon-based login. Macaroon tokens
            acquired when logging will be saved to bakery_client.cookies.
            If this is None, a default bakery_client will be used.
        :param asyncio.BaseEventLoop loop: The event loop to use for async
            operations.
        :param int max_frame_size: The maximum websocket frame size to allow.
        :param int retries: When connecting or reconnecting, and all endpoints
            fail, how many times to retry the connection before giving up.
        :param int retry_backoff: Number of seconds to increase the wait
            between connection retry attempts (a backoff of 10 with 3 retries
            would wait 10s, 20s, and 30s).
        """
        self = cls()
        if endpoint is None:
            raise ValueError('no endpoint provided')
        self.uuid = uuid
        if bakery_client is None:
            bakery_client = httpbakery.Client()
        self.bakery_client = bakery_client
        if username and '@' in username and not username.endswith('@local'):
            # We're trying to log in as an external user - we need to use
            # macaroon authentication with no username or password.
            if password is not None:
                raise errors.JujuAuthError('cannot log in as external '
                                           'user with a password')
            username = None
        self.usertag = tag.user(username)
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

        self._retries = retries
        self._retry_backoff = retry_backoff

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
        context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH, cadata=cert)
        if cert:
            # Disable hostname checking if and only if we have an explicit cert
            # to validate against, because the cert doesn't contain the IP addr
            # of the controller, which is what self-bootstrapped controllers
            # use. And because we pre-share and trust both the cert and
            # endpoint address anyway, it's safe to skip that check.
            # See: https://github.com/juju/python-libjuju/issues/302
            context.check_hostname = False
        return context

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
        ), url, endpoint, cacert)

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
        try:
            while True:
                await utils.run_with_interrupt(
                    _do_ping(),
                    self.monitor.close_called,
                    loop=self.loop)
                if self.monitor.close_called.is_set():
                    break
        except websockets.exceptions.ConnectionClosed:
            # The connection has closed - we can't do anything
            # more until the connection is restarted.
            log.debug('ping failed because of closed connection')
            pass

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
            if self.monitor.status == Monitor.DISCONNECTED:
                # closed cleanly; shouldn't try to reconnect
                raise websockets.exceptions.ConnectionClosed(
                    0, 'websocket closed')
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
                if self.monitor.status != Monitor.CONNECTED:
                    # reconnect failed; abort and shutdown
                    log.error('RPC: Automatic reconnect failed')
                    raise
        result = await self._recv(msg['request-id'])
        log.debug('connection {} <- {}'.format(id(self), result))

        if not result:
            return result

        if 'error' in result:
            # API Error Response
            raise errors.JujuAPIError(result)

        if 'response' not in result:
            # This may never happen
            return result

        if 'results' in result['response']:
            # Check for errors in a result list.
            # TODO This loses the results that might have succeeded.
            # Perhaps JujuError should return all the results including
            # errors, or perhaps a keyword parameter to the rpc method
            # could be added to trigger this behaviour.
            err_results = []
            for res in result['response']['results']:
                if res.get('error', {}).get('message'):
                    err_results.append(res['error']['message'])
            if err_results:
                raise errors.JujuError(err_results)

        elif result['response'].get('error', {}).get('message'):
            raise errors.JujuError(result['response']['error']['message'])

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
        return await Connection.connect(**self.connect_params())

    def connect_params(self):
        """Return a tuple of parameters suitable for passing to
        Connection.connect that can be used to make a new connection
        to the same controller (and model if specified. The first
        element in the returned tuple holds the endpoint argument;
        the other holds a dict of the keyword args.
        """
        return {
            'endpoint': self.endpoint,
            'uuid': self.uuid,
            'username': self.username,
            'password': self.password,
            'cacert': self.cacert,
            'bakery_client': self.bakery_client,
            'loop': self.loop,
            'max_frame_size': self.max_frame_size,
        }

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
            raise errors.JujuConnectionError('no endpoints to connect to')

        async def _try_endpoint(endpoint, cacert, delay):
            if delay:
                await asyncio.sleep(delay)
            return await self._open(endpoint, cacert)

        # Try all endpoints in parallel, with slight increasing delay (+100ms
        # for each subsequent endpoint); the delay allows us to prefer the
        # earlier endpoints over the latter. Use first successful connection.
        tasks = [self.loop.create_task(_try_endpoint(endpoint, cacert,
                                                     0.1 * i))
                 for i, (endpoint, cacert) in enumerate(endpoints)]
        for attempt in range(self._retries + 1):
            for task in asyncio.as_completed(tasks, loop=self.loop):
                try:
                    result = await task
                    break
                except ConnectionError:
                    continue  # ignore; try another endpoint
            else:
                _endpoints_str = ', '.join([endpoint
                                            for endpoint, cacert in endpoints])
                if attempt < self._retries:
                    log.debug('Retrying connection to endpoints: {}; '
                              'attempt {} of {}'.format(_endpoints_str,
                                                        attempt + 1,
                                                        self._retries + 1))
                    await asyncio.sleep((attempt + 1) * self._retry_backoff)
                    continue
                else:
                    raise errors.JujuConnectionError(
                        'Unable to connect to any endpoint: '
                        '{}'.format(_endpoints_str))
            # only executed if inner loop's else did not continue
            # (i.e., inner loop did break due to successful connection)
            break
        for task in tasks:
            task.cancel()
        self.ws = result[0]
        self.addr = result[1]
        self.endpoint = result[2]
        self.cacert = result[3]
        self._receiver_task.start()
        log.debug("Driver connected to juju %s", self.addr)
        self.monitor.close_called.clear()

    async def _connect_with_login(self, endpoints):
        """Connect to the websocket.

        If uuid is None, the connection will be to the controller. Otherwise it
        will be to the model.
        :return: The response field of login response JSON object.
        """
        success = False
        try:
            await self._connect(endpoints)
            # It's possible that we may get several discharge-required errors,
            # corresponding to different levels of authentication, so retry
            # a few times.
            for i in range(0, 2):
                result = (await self.login())['response']
                macaroonJSON = result.get('discharge-required')
                if macaroonJSON is None:
                    self.info = result
                    success = True
                    return result
                macaroon = bakery.Macaroon.from_dict(macaroonJSON)
                self.bakery_client.handle_error(
                    httpbakery.Error(
                        code=httpbakery.ERR_DISCHARGE_REQUIRED,
                        message=result.get('discharge-required-error'),
                        version=macaroon.version,
                        info=httpbakery.ErrorInfo(
                            macaroon=macaroon,
                            macaroon_path=result.get('macaroon-path'),
                        ),
                    ),
                    # note: remove the port number.
                    'https://' + self.endpoint + '/',
                )
            raise errors.JujuAuthError('failed to authenticate '
                                       'after several attempts')
        finally:
            if not success:
                await self.close()

    async def _connect_with_redirect(self, endpoints):
        try:
            login_result = await self._connect_with_login(endpoints)
        except errors.JujuRedirectException as e:
            # Bubble up exception if the client should not follow the redirect
            if e.follow_redirect is False:
                raise
            login_result = await self._connect_with_login(e.endpoints)
        self._build_facades(login_result.get('facades', {}))
        self._pinger_task.start()

    def _build_facades(self, facades):
        self.facades.clear()
        for facade in facades:
            self.facades[facade['name']] = facade['versions'][-1]

    async def login(self):
        params = {}
        params['auth-tag'] = self.usertag
        if self.password:
            params['credentials'] = self.password
        else:
            macaroons = _macaroons_for_domain(self.bakery_client.cookies,
                                              self.endpoint)
            params['macaroons'] = [[bakery.macaroon_to_dict(m) for m in ms]
                                   for ms in macaroons]

        try:
            return await self.rpc({
                "type": "Admin",
                "request": "Login",
                "version": 3,
                "params": params,
            })
        except errors.JujuAPIError as e:
            if e.error_code != 'redirection required':
                raise
            log.info('Controller requested redirect')
            # Check if the redirect error provides a payload with embedded
            # redirection info (juju 2.6+ controller). In this case, return a
            # redirect exception which the library should not automatically
            # follow but rather bubble up to the user. This matches the
            # behaviour of juju cli whereas for JAAS-like redirects we will
            # need to make an extra RPC call to get the redirect info.
            if e.error_info is not None:
                raise errors.JujuRedirectException(e.error_info, False) from e

            # Fetch additional redirection information now so that
            # we can safely close the connection after login
            # fails.
            redirect_info = (await self.rpc({
                "type": "Admin",
                "request": "RedirectInfo",
                "version": 3,
            }))['response']
            raise errors.JujuRedirectException(redirect_info, True) from e


class _Task:
    def __init__(self, task, loop):
        self.stopped = asyncio.Event(loop=loop)
        self.stopped.set()
        self.task = task
        self.loop = loop

    def start(self):
        async def run():
            try:
                return await self.task()
            finally:
                self.stopped.set()
        self.stopped.clear()
        self.loop.create_task(run())


def _macaroons_for_domain(cookies, domain):
    '''Return any macaroons from the given cookie jar that
    apply to the given domain name.'''
    req = urllib.request.Request('https://' + domain + '/')
    cookies.add_cookie_header(req)
    return httpbakery.extract_macaroons(req)
