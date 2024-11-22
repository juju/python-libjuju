# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
from __future__ import annotations

import base64
import json
import logging
import ssl
import urllib.request
import warnings
import weakref
from http.client import HTTPSConnection
from typing import Any, Literal, Sequence

import macaroonbakery.bakery as bakery
import macaroonbakery.httpbakery as httpbakery
import websockets
from dateutil.parser import parse
from typing_extensions import Self, TypeAlias, overload
from websockets.protocol import State

from juju import errors, jasyncio, tag, utils
from juju.client import client
from juju.utils import IdQueue
from juju.version import CLIENT_VERSION

from .facade import TypeEncoder, _Json, _RichJson
from .facade_versions import client_facade_versions, known_unsupported_facades

SpecifiedFacades: TypeAlias = "dict[str, dict[Literal['versions'], Sequence[int]]]"
_WebSocket: TypeAlias = websockets.WebSocketClientProtocol

LEVELS = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR"]
log = logging.getLogger("juju.client.connection")


class Monitor:
    """Monitor helper class for our Connection class.

    Contains a reference to an instantiated Connection, along with a
    reference to the Connection.receiver Future. Upon inspection of
    these objects, this class determines whether the connection is in
    an 'error', 'connected' or 'disconnected' state.

    Use this class to stay up to date on the health of a connection,
    and take appropriate action if the connection errors out due to
    network issues or other unexpected circumstances.

    """

    ERROR = "error"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"

    def __init__(self, connection: Connection):
        self.connection = weakref.ref(connection)
        self.reconnecting = jasyncio.Lock()
        self.close_called = jasyncio.Event()

    @property
    def status(self):
        """Determine the status of the connection and receiver, and return
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
        if not connection._ws:
            return self.DISCONNECTED

        # close called but not yet complete
        if self.close_called.is_set():
            return self.DISCONNECTING

        # connection closed uncleanly (we didn't call connection.close)
        if connection.is_debug_log_connection:
            stopped = connection._debug_log_task.cancelled()
        else:
            stopped = (
                connection._receiver_task is not None
                and connection._receiver_task.cancelled()
            )

        if stopped or connection._ws.state is not State.OPEN:
            return self.ERROR

        # everything is fine!
        return self.CONNECTED


class Connection:
    """Usage::

    # Connect to an arbitrary api server
    client = await Connection.connect(
        api_endpoint, model_uuid, username, password, cacert)

    """

    MAX_FRAME_SIZE = 2**22
    "Maximum size for a single frame.  Defaults to 4MB."
    facades: dict[str, int]
    _specified_facades: dict[str, Sequence[int]]
    bakery_client: Any
    usertag: str | None
    password: str | None
    name: str
    __request_id__: int
    endpoints: list[tuple[str, str]] | None  # Set by juju/controller.py
    is_debug_log_connection: bool
    monitor: Monitor
    proxy: Any  # Need to find types for this library
    max_frame_size: int
    _retries: int
    _retry_backoff: float
    uuid: str | None
    messages: IdQueue
    _ws: _WebSocket | None

    @classmethod
    async def connect(
        cls,
        endpoint=None,
        uuid: str | None = None,
        username: str | None = None,
        password: str | None = None,
        cacert=None,
        bakery_client=None,
        max_frame_size: int | None = None,
        retries=3,
        retry_backoff=10,
        specified_facades: SpecifiedFacades | None = None,
        proxy=None,
        debug_log_conn=None,
        debug_log_params={},
    ) -> Self:
        """Connect to the websocket.

        If uuid is None, the connection will be to the controller. Otherwise it
        will be to the model.

        :param str endpoint: The hostname:port of the controller to connect to (or list of strings).
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
        :param int max_frame_size: The maximum websocket frame size to allow.
        :param int retries: When connecting or reconnecting, and all endpoints
            fail, how many times to retry the connection before giving up.
        :param int retry_backoff: Number of seconds to increase the wait
            between connection retry attempts (a backoff of 10 with 3 retries
            would wait 10s, 20s, and 30s).
        :param specified_facades: (deprecated) define a series of facade versions you wish to override
            to prevent using the conservative client pinning with in the client.
        :param TextIOWrapper debug_log_conn: target if this is a debug log connection
        :param dict debug_log_params: filtering parameters for the debug-log output
        """
        self = cls()
        if endpoint is None:
            raise ValueError("no endpoint provided")
        if not isinstance(endpoint, str) and not isinstance(endpoint, list):
            raise TypeError("Endpoint should be either str or list")
        self.uuid = uuid
        if bakery_client is None:
            bakery_client = httpbakery.Client()
        self.bakery_client = bakery_client
        if username and "@" in username and not username.endswith("@local"):
            # We're trying to log in as an external user - we need to use
            # macaroon authentication with no username or password.
            if password is not None:
                raise errors.JujuAuthError(
                    "cannot log in as external user with a password"
                )
            username = None
        self.usertag = tag.user(username)
        self.password = password

        self.__request_id__ = 0

        # The following instance variables are initialized by the
        # _connect_with_redirect method, but create them here
        # as a reminder that they will exist.
        self.addr = None
        self._ws = None
        self.endpoint = None
        self.endpoints = None
        self.cacert = None
        self.info = None

        self.debug_log_target = debug_log_conn
        self.is_debug_log_connection = debug_log_conn is not None
        self.debug_log_params = debug_log_params
        self.debug_log_shown_lines = 0  # number of lines

        # Create that _Task objects but don't start the tasks yet.
        self._pinger_task = None
        self._receiver_task = None
        self._debug_log_task = None

        self._retries = retries
        self._retry_backoff = retry_backoff

        self.facades = {}

        if specified_facades:
            warnings.warn(
                "The `specified_facades` argument is deprecated and will be removed soon",
                DeprecationWarning,
                stacklevel=3,
            )
            self._specified_facades = {
                name: d["versions"] for name, d in specified_facades.items()
            }
        else:
            self._specified_facades = {}

        self.messages = IdQueue()
        self.monitor = Monitor(connection=self)
        if max_frame_size is None:
            max_frame_size = self.MAX_FRAME_SIZE
        self.max_frame_size = max_frame_size

        self.proxy = proxy
        if self.proxy is not None:
            self.proxy.connect()

        _endpoints = (
            [(endpoint, cacert)]
            if isinstance(endpoint, str)
            else [(e, cacert) for e in endpoint]
        )
        last_error = None
        for _ep in _endpoints:
            try:
                if self.is_debug_log_connection:
                    # make a direct connection with basic auth if
                    # debug-log (i.e. no redirection or login)
                    await self._connect([_ep])
                else:
                    await self._connect_with_redirect([_ep])
                return self
            except ssl.SSLError as e:
                last_error = e
                continue
            except OSError as e:
                logging.debug(f"Cannot access endpoint {_ep}: {e.strerror}")
                last_error = e
                continue
        if last_error is not None:
            raise last_error
        raise Exception("Unable to connect to websocket")

    @property
    def ws(self):
        log.warning(
            "Direct access to the websocket object may cause disruptions in asyncio event handling."
        )
        return self._ws

    @property
    def username(self) -> str | None:
        if not self.usertag:
            return None
        return self.usertag[len("user-") :]

    @property
    def is_using_old_client(self):
        if self.info is None:
            raise errors.JujuError("Not connected yet.")
        return self.info["server-version"].startswith("2.")

    @property
    def is_open(self):
        return self.monitor.status == Monitor.CONNECTED

    def _get_ssl(self, cert: str | None = None) -> ssl.SSLContext:
        context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH, cadata=cert
        )
        if cert:
            # Disable hostname checking if and only if we have an explicit cert
            # to validate against, because the cert doesn't contain the IP addr
            # of the controller, which is what self-bootstrapped controllers
            # use. And because we pre-share and trust both the cert and
            # endpoint address anyway, it's safe to skip that check.
            # See: https://github.com/juju/python-libjuju/issues/302
            context.check_hostname = False
        return context

    async def _open(
        self, endpoint: str, cacert: str
    ) -> tuple[_WebSocket, str, str, str]:
        if self.is_debug_log_connection:
            assert self.uuid
            url = f"wss://user-{self.username}:{self.password}@{endpoint}/model/{self.uuid}/log"
        elif self.uuid:
            url = f"wss://{endpoint}/model/{self.uuid}/api"
        else:
            url = f"wss://{endpoint}/api"

        # We need to establish a server_hostname here for TLS sni if we are
        # connecting through a proxy as the Juju controller certificates will
        # not be covering the proxy
        sock = None
        server_hostname = None
        if self.proxy is not None:
            sock = self.proxy.socket()
            server_hostname = "juju-app"

        return (
            (
                await websockets.connect(
                    url,
                    ssl=self._get_ssl(cacert),
                    max_size=self.max_frame_size,
                    server_hostname=server_hostname,
                    sock=sock,
                )
            ),
            url,
            endpoint,
            cacert,
        )

    async def close(self, to_reconnect: bool = False):
        if not self._ws:
            return
        self.monitor.close_called.set()

        # Cancel all the tasks (that we started):
        tasks_need_to_be_gathered = []
        if self._pinger_task:
            tasks_need_to_be_gathered.append(self._pinger_task)
            self._pinger_task.cancel()
        if self._receiver_task:
            tasks_need_to_be_gathered.append(self._receiver_task)
            self._receiver_task.cancel()
        if self._debug_log_task:
            tasks_need_to_be_gathered.append(self._debug_log_task)
            self._debug_log_task.cancel()

        await self._ws.close()

        if not to_reconnect:
            try:
                log.debug("Gathering all tasks for connection close")
                await jasyncio.gather(*tasks_need_to_be_gathered)
            except jasyncio.CancelledError:
                pass
            except websockets.exceptions.ConnectionClosed:
                pass

        self._pinger_task = None
        self._receiver_task = None
        self._debug_log_task = None

        if self.proxy is not None:
            self.proxy.close()

    async def _recv(self, request_id: int) -> dict[str, Any]:
        if not self.is_open:
            raise websockets.exceptions.ConnectionClosedOK(None, None)
        try:
            return await self.messages.get(request_id)
        except GeneratorExit:
            return {}

    def debug_log_filter_write(self, result):
        write_or_not = True

        entity = result["tag"]
        msg_lev = result["sev"]
        mod = result["mod"]
        msg = result["msg"]

        excluded_entities = self.debug_log_params["exclude"]
        excluded_modules = self.debug_log_params["exclude_module"]
        write_or_not = (
            write_or_not
            and (mod not in excluded_modules)
            and (entity not in excluded_entities)
        )

        included_entities = self.debug_log_params["include"]
        only_these_modules = self.debug_log_params["include_module"]
        write_or_not = (
            write_or_not
            and (only_these_modules == [] or mod in only_these_modules)
            and (included_entities == [] or entity in included_entities)
        )

        log_level = self.debug_log_params["level"]

        if log_level != "" and log_level not in LEVELS:
            log.warning(
                "Debug Logger: level should be one of %s, given %s"
                % (LEVELS, log_level)
            )
        else:
            write_or_not = write_or_not and (
                log_level == "" or (LEVELS.index(msg_lev) >= LEVELS.index(log_level))
            )

        # TODO
        # lines = self.debug_log_params['lines']
        # no_tail = self.debug_log_params['no_tail']

        if write_or_not:
            ts = parse(result["ts"])

            self.debug_log_target.write(
                "%s %02d:%02d:%02d %s %s %s\n"
                % (entity, ts.hour, ts.minute, ts.second, msg_lev, mod, msg)
            )
            return 1
        else:
            return 0

    async def _debug_logger(self):
        try:
            while self.is_open:
                result = await utils.run_with_interrupt(
                    self._ws.recv(), self.monitor.close_called, log=log
                )
                if self.monitor.close_called.is_set():
                    break
                if result is not None and result != "{}\n":
                    result = json.loads(result)

                    number_of_lines_written = self.debug_log_filter_write(result)

                    self.debug_log_shown_lines += number_of_lines_written

                    if self.debug_log_shown_lines >= self.debug_log_params["limit"]:
                        jasyncio.create_task(self.close(), name="Task_Close")
                        return

        except KeyError as e:
            log.exception("Unexpected debug line -- %s" % e)
            jasyncio.create_task(self.close(), name="Task_Close")
            raise
        except jasyncio.CancelledError:
            jasyncio.create_task(self.close(), name="Task_Close")
            raise
        except websockets.exceptions.ConnectionClosed:
            log.warning("Debug Logger: Connection closed, reconnecting")
            # the reconnect has to be done as a task because the receiver will
            # be cancelled by the reconnect and we don't want the reconnect
            # to be aborted half-way through
            jasyncio.ensure_future(self.reconnect())
            return
        except Exception as e:
            log.exception("Error in debug logger : %s" % e)
            jasyncio.create_task(self.close(), name="Task_Close")
            raise

    async def _receiver(self):
        try:
            while self.is_open:
                result = await utils.run_with_interrupt(
                    self._ws.recv(), self.monitor.close_called, log=log
                )
                if self.monitor.close_called.is_set():
                    break
                if result is not None:
                    result = json.loads(result)
                    await self.messages.put(result["request-id"], result)
        except jasyncio.CancelledError:
            log.debug("Receiver: Cancelled")
            pass
        except websockets.exceptions.ConnectionClosed as e:
            log.warning("Receiver: Connection closed, reconnecting")
            await self.messages.put_all(e)
            # the reconnect has to be done as a task because the receiver will
            # be cancelled by the reconnect and we don't want the reconnect
            # to be aborted half-way through
            jasyncio.ensure_future(self.reconnect())
            return
        except Exception as e:
            log.exception("Error in receiver")
            # make pending listeners aware of the error
            await self.messages.put_all(e)
            raise

    async def _pinger(self):
        """A Controller can time us out if we are silent for too long. This
        is especially true in JaaS, which has a fairly strict timeout.

        To prevent timing out, we send a ping every ten seconds.

        """

        async def _do_ping():
            try:
                log.debug(f"Pinger {self._pinger_task}: pinging")
                await pinger_facade.Ping()
            except jasyncio.CancelledError:
                raise

        pinger_facade = client.PingerFacade.from_connection(self)
        try:
            while True:
                await utils.run_with_interrupt(
                    _do_ping(), self.monitor.close_called, log=log
                )
                if self.monitor.close_called.is_set():
                    break
                await jasyncio.sleep(10)
        except jasyncio.CancelledError:
            log.debug("Pinger: Cancelled")
            pass
        except websockets.exceptions.ConnectionClosed:
            # The connection has closed - we can't do anything
            # more until the connection is restarted.
            log.debug("ping failed because of closed connection")
            pass

    @overload
    async def rpc(
        self, msg: dict[str, _Json], encoder: None = None
    ) -> dict[str, _Json]: ...

    @overload
    async def rpc(
        self, msg: dict[str, _RichJson], encoder: TypeEncoder
    ) -> dict[str, _Json]: ...

    async def rpc(
        self, msg: dict[str, Any], encoder: json.JSONEncoder | None = None
    ) -> dict[str, _Json]:
        """Make an RPC to the API. The message is encoded as JSON
        using the given encoder if any.
        :param msg: Parameters for the call (will be encoded as JSON).
        :param encoder: Encoder to be used when encoding the message.
        :return: The result of the call.
        :raises JujuAPIError: When there's an error returned.
        :raises JujuError:
        """
        self.__request_id__ += 1
        msg["request-id"] = self.__request_id__
        if "params" not in msg:
            msg["params"] = {}
        if "version" not in msg:
            msg["version"] = self.facades[msg["type"]]
        outgoing = json.dumps(msg, indent=2, cls=encoder)
        log.debug(f"connection id: {id(self)} ---> {outgoing}")
        for attempt in range(3):
            if self.monitor.status == Monitor.DISCONNECTED:
                # closed cleanly; shouldn't try to reconnect
                raise websockets.exceptions.ConnectionClosed(
                    websockets.frames.Close(
                        websockets.frames.CloseCode.NORMAL_CLOSURE, "websocket closed"
                    )
                )
            try:
                await self._ws.send(outgoing)
                break
            except websockets.ConnectionClosed:
                if attempt == 2:
                    raise
                log.warning("RPC: Connection closed, reconnecting")
                # the reconnect has to be done in a separate task because,
                # if it is triggered by the pinger, then this RPC call will
                # be cancelled when the pinger is cancelled by the reconnect,
                # and we don't want the reconnect to be aborted halfway through
                await jasyncio.wait([jasyncio.create_task(self.reconnect())])
                if self.monitor.status != Monitor.CONNECTED:
                    # reconnect failed; abort and shutdown
                    log.error("RPC: Automatic reconnect failed")
                    raise
        result = await self._recv(msg["request-id"])
        log.debug(f"connection id : {id(self)} <--- {result}")

        if not result:
            return result

        if "error" in result:
            # API Error Response
            raise errors.JujuAPIError(result)

        if "response" not in result:
            # This may never happen
            return result

        if "results" in result["response"]:
            # Check for errors in a result list.
            # TODO This loses the results that might have succeeded.
            # Perhaps JujuError should return all the results including
            # errors, or perhaps a keyword parameter to the rpc method
            # could be added to trigger this behaviour.
            err_results = [
                res["error"]["message"]
                for res in (result["response"]["results"] or [])
                if res.get("error", {}).get("message")
            ]
            if err_results:
                raise errors.JujuError(err_results)

        elif result["response"].get("error", {}).get("message"):
            raise errors.JujuError(result["response"]["error"]["message"])

        return result

    def _http_headers(self) -> dict[str, str]:
        """Return dictionary of http headers necessary for making an http
        connection to the endpoint of this Connection.

        :return: Dictionary of headers

        """
        if not self.usertag:
            return {}

        creds = "{}:{}".format(self.usertag, self.password or "")
        token = base64.b64encode(creds.encode())
        return {"Authorization": f"Basic {token.decode()}"}

    def https_connection(self) -> tuple[HTTPSConnection, dict[str, str], str]:
        """Return an https connection to this Connection's endpoint.

        Returns a 3-tuple containing::

            1. The :class:`HTTPSConnection` instance
            2. Dictionary of auth headers to be used with the connection
            3. The root url path (str) to be used for requests.

        """
        endpoint = self.endpoint
        # Support IPv6 by right splitting on : and removing [] around IP address for host
        host, remainder = endpoint.rsplit(":", 1)
        host = host.strip("[]")
        port = remainder
        if "/" in remainder:
            port, _ = remainder.split("/", 1)

        conn = HTTPSConnection(
            host,
            int(port),
            context=self._get_ssl(self.cacert),
        )

        path = f"/model/{self.uuid}" if self.uuid else ""
        return conn, self._http_headers(), path

    async def clone(self):
        """Return a new Connection, connected to the same websocket endpoint
        as this one.

        """
        return await Connection.connect(**self.connect_params())

    def connect_params(self):
        """Return a dict of parameters suitable for passing to
        Connection.connect that can be used to make a new connection
        to the same controller (and model if specified).
        """
        return {
            "endpoint": self.endpoint,
            "uuid": self.uuid,
            "username": self.username,
            "password": self.password,
            "cacert": self.cacert,
            "bakery_client": self.bakery_client,
            "max_frame_size": self.max_frame_size,
            "proxy": self.proxy,
        }

    async def controller(self):
        """Return a Connection to the controller at self.endpoint"""
        return await Connection.connect(
            self.endpoint,
            username=self.username,
            password=self.password,
            cacert=self.cacert,
            bakery_client=self.bakery_client,
            max_frame_size=self.max_frame_size,
        )

    async def reconnect(self):
        """Force a reconnection."""
        monitor = self.monitor
        if monitor.reconnecting.locked() or monitor.close_called.is_set():
            return
        async with monitor.reconnecting:
            await self.close(to_reconnect=True)
            connector = (
                self._connect
                if self.is_debug_log_connection
                else self._connect_with_login
            )
            res = await connector(
                [(self.endpoint, self.cacert)] if not self.endpoints else self.endpoints
            )
            if not self.is_debug_log_connection:
                self._build_facades(res.get("facades", {}))
                if not self._pinger_task:
                    log.debug("reconnect: scheduling a pinger task")
                    self._pinger_task = jasyncio.create_task(
                        self._pinger(), name="Task_Pinger"
                    )

    async def _connect(self, endpoints):
        if len(endpoints) == 0:
            raise errors.JujuConnectionError("no endpoints to connect to")

        async def _try_endpoint(
            endpoint, cacert, delay
        ) -> tuple[_WebSocket, str, str, str]:
            if delay:
                await jasyncio.sleep(delay)
            return await self._open(endpoint, cacert)

        # Try all endpoints in parallel, with slight increasing delay (+100ms
        # for each subsequent endpoint); the delay allows us to prefer the
        # earlier endpoints over the latter. Use first successful connection.
        tasks = [
            jasyncio.ensure_future(_try_endpoint(endpoint, cacert, 0.1 * i))
            for i, (endpoint, cacert) in enumerate(endpoints)
        ]
        result: tuple[_WebSocket, str, str, str] | None = None

        for attempt in range(self._retries + 1):
            for task in jasyncio.as_completed(tasks):
                try:
                    result = await task
                    break
                except ConnectionError:
                    continue  # ignore; try another endpoint
            else:
                _endpoints_str = ", ".join([endpoint for endpoint, cacert in endpoints])
                if attempt < self._retries:
                    log.debug(
                        f"Retrying connection to endpoints: {_endpoints_str}; attempt {attempt + 1} of {self._retries + 1}"
                    )
                    await jasyncio.sleep((attempt + 1) * self._retry_backoff)
                    continue
                else:
                    raise errors.JujuConnectionError(
                        f"Unable to connect to any endpoint: {_endpoints_str}"
                    )
            # only executed if inner loop's else did not continue
            # (i.e., inner loop did break due to successful connection)
            break

        for task in tasks:
            task.cancel()

        assert result  # loop raises or sets the result

        self._ws = result[0]
        self.addr = result[1]
        self.endpoint = result[2]
        self.cacert = result[3]

        #  If this is a debug-log connection, and the _debug_log_task
        #  is not created yet, then go ahead and schedule it
        if self.is_debug_log_connection and not self._debug_log_task:
            self._debug_log_task = jasyncio.create_task(
                self._debug_logger(), name="Task_Debug_Log"
            )

        #  If this is regular connection, and we dont have a
        #  receiver_task yet, then schedule a _receiver_task
        elif not self.is_debug_log_connection and not self._receiver_task:
            log.debug("_connect: scheduling a receiver task")
            self._receiver_task = jasyncio.create_task(
                self._receiver(), name="Task_Receiver"
            )

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
            for _ in range(0, 2):
                result = (await self.login())["response"]
                macaroon_json = result.get("discharge-required")
                if macaroon_json is None:
                    self.info = result
                    success = True
                    return result
                macaroon = bakery.Macaroon.from_dict(macaroon_json)
                self.bakery_client.handle_error(
                    httpbakery.Error(
                        code=httpbakery.ERR_DISCHARGE_REQUIRED,
                        message=result.get("discharge-required-error"),
                        version=macaroon.version,
                        info=httpbakery.ErrorInfo(
                            macaroon=macaroon,
                            macaroon_path=result.get("macaroon-path"),
                        ),
                    ),
                    # note: remove the port number.
                    "https://" + self.endpoint + "/",
                )
            raise errors.JujuAuthError("failed to authenticate after several attempts")
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
        self._build_facades(login_result.get("facades", {}))
        if not self._pinger_task:
            log.debug("_connect_with_redirect: scheduling a pinger task")
            self._pinger_task = jasyncio.create_task(self._pinger(), name="Task_Pinger")

    # _build_facades takes the facade list that comes from the connection with the controller,
    # validates that the client knows about them (client_facade_versions) and builds the facade list
    # (into the self._specified facades) with the max versions that both the client and the controller
    # can negotiate on
    def _build_facades(self, facades_from_connection):
        self.facades.clear()
        for facade in facades_from_connection:
            name = facade["name"]
            if name in self._specified_facades:
                client_versions = self._specified_facades[name]
            elif name in client_facade_versions:
                client_versions = client_facade_versions[name]
            elif name in known_unsupported_facades:
                continue
            else:
                log.warning(f"unexpected facade {name} received from the controller")
                continue

            controller_versions = facade["versions"]
            candidates = set(client_versions) & set(controller_versions)
            if not candidates:
                log.warning(
                    f"unknown common facade version for {name},\n"
                    f"versions known to client : {client_versions}\n"
                    f"versions known to controller : {controller_versions}"
                )
                continue
            self.facades[name] = max(candidates)

    async def login(self):
        params = {}
        # Set the client version
        params["client-version"] = CLIENT_VERSION
        params["auth-tag"] = self.usertag
        if self.password:
            params["credentials"] = self.password
        else:
            macaroons = _macaroons_for_domain(self.bakery_client.cookies, self.endpoint)
            params["macaroons"] = [
                [bakery.macaroon_to_dict(m) for m in ms] for ms in macaroons
            ]

        try:
            return await self.rpc({
                "type": "Admin",
                "request": "Login",
                "version": 3,
                "params": params,
            })
        except errors.JujuAPIError as e:
            if e.error_code != "redirection required":
                raise
            log.info("Controller requested redirect")
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
            redirect_info = (
                await self.rpc({
                    "type": "Admin",
                    "request": "RedirectInfo",
                    "version": 3,
                })
            )["response"]
            raise errors.JujuRedirectException(redirect_info, True) from e


def _macaroons_for_domain(cookies, domain):
    """Return any macaroons from the given cookie jar that
    apply to the given domain name.
    """
    req = urllib.request.Request("https://" + domain + "/")
    cookies.add_cookie_header(req)
    return httpbakery.extract_macaroons(req)
