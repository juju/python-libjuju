# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import base64
import json
import logging
import ssl
import signal
import urllib.request
import weakref
from http.client import HTTPSConnection
from dateutil.parser import parse

import macaroonbakery.bakery as bakery
import macaroonbakery.httpbakery as httpbakery
import websockets
from juju import errors, tag, utils, jasyncio
from juju.client import client
from juju.utils import IdQueue
from juju.version import TARGET_JUJU_VERSION

log = logging.getLogger('juju.client.connection')

# Please keep in alphabetical order
client_facades = {
    'Action': {'versions': [2, 6, 7]},
    'ActionPruner': {'versions': [1]},
    'Agent': {'versions': [2, 3]},
    'AgentLifeFlag': {'versions': [1]},
    'AgentTools': {'versions': [1]},
    'AllModelWatcher': {'versions': [2, 3, 4]},
    'AllWatcher': {'versions': [1, 2, 3, 4]},
    'Annotations': {'versions': [2]},
    'Application': {'versions': [14, 15, 16, 17, 19]},
    'ApplicationOffers': {'versions': [1, 2, 4]},
    'ApplicationScaler': {'versions': [1]},
    'Backups': {'versions': [1, 2, 3]},
    'Block': {'versions': [2]},
    'Bundle': {'versions': [5, 6]},
    'CharmHub': {'versions': [1]},
    'CharmRevisionUpdater': {'versions': [2]},
    'CharmDownloader': {'versions': [1]},
    'Charms': {'versions': [5, 6]},
    'Cleaner': {'versions': [2]},
    'Client': {'versions': [5, 6]},
    'Cloud': {'versions': [1, 2, 3, 4, 5, 7]},
    'Controller': {'versions': [9, 11]},
    'CrossModelRelations': {'versions': [1, 2]},
    'CrossModelSecrets': {'versions': [1]},
    'CrossController': {'versions': [1]},
    'CredentialManager': {'versions': [1]},
    'CredentialValidator': {'versions': [1, 2]},
    'CAASAdmission': {'versions': [1]},
    'CAASAgent': {'versions': [1, 2]},
    'CAASApplication': {'versions': [1]},
    'CAASApplicationProvisioner': {'versions': [1]},
    'CAASFirewaller': {'versions': [1]},
    'CAASFirewallerEmbedded': {'versions': [1]},
    'CAASFirewallerSidecar': {'versions': [1]},
    'CAASModelOperator': {'versions': [1]},
    'CAASModelConfigManager': {'versions': [1]},
    'CAASOperator': {'versions': [1]},
    'CAASOperatorProvisioner': {'versions': [1]},
    'CAASOperatorUpgrader': {'versions': [1]},
    'CAASUnitProvisioner': {'versions': [1, 2]},
    'Deployer': {'versions': [1]},
    'DiskManager': {'versions': [2]},
    'EntityWatcher': {'versions': [2]},
    'EnvironUpgrader': {'versions': [1]},
    'ExternalControllerUpdater': {'versions': [1]},
    'FanConfigurer': {'versions': [1]},
    'FilesystemAttachmentsWatcher': {'versions': [2]},
    'Firewaller': {'versions': [3, 4, 5, 7]},
    'FirewallRules': {'versions': [1]},
    'HighAvailability': {'versions': [2]},
    'HostKeyReporter': {'versions': [1]},
    'ImageManager': {'versions': [2]},
    'ImageMetadata': {'versions': [3]},
    'ImageMetadataManager': {'versions': [1]},
    'InstanceMutater': {'versions': [2, 3]},
    'InstancePoller': {'versions': [3, 4]},
    'KeyManager': {'versions': [1]},
    'KeyUpdater': {'versions': [1]},
    'LeadershipService': {'versions': [2]},
    'LifeFlag': {'versions': [1]},
    'Logger': {'versions': [1]},
    'LogForwarding': {'versions': [1]},
    'Machiner': {'versions': [1, 2, 5]},
    'MachineActions': {'versions': [1]},
    'MachineManager': {'versions': [9, 10]},
    'MachineUndertaker': {'versions': [1]},
    'MeterStatus': {'versions': [1, 2]},
    'MetricsAdder': {'versions': [2]},
    'MetricsDebug': {'versions': [2]},
    'MetricsManager': {'versions': [1]},
    'MigrationFlag': {'versions': [1]},
    'MigrationMaster': {'versions': [1, 3]},
    'MigrationMinion': {'versions': [1]},
    'MigrationStatusWatcher': {'versions': [1]},
    'MigrationTarget': {'versions': [1]},
    'ModelConfig': {'versions': [1, 2, 3]},
    'ModelGeneration': {'versions': [1, 2, 4]},
    'ModelManager': {'versions': [2, 3, 4, 5, 9]},
    'ModelSummaryWatcher': {'versions': [1]},
    'ModelUpgrader': {'versions': [1]},
    'NotifyWatcher': {'versions': [1]},
    'OfferStatusWatcher': {'versions': [1]},
    'Payloads': {'versions': [1]},
    'PayloadsHookContext': {'versions': [1]},
    'Pinger': {'versions': [1]},
    'Provisioner': {'versions': [11]},
    'ProxyUpdater': {'versions': [1, 2]},
    'RaftLease': {'versions': [1, 2]},
    'Reboot': {'versions': [2]},
    'RelationStatusWatcher': {'versions': [1]},
    'RelationUnitsWatcher': {'versions': [1]},
    'RemoteRelations': {'versions': [1, 2]},
    'RemoteRelationWatcher': {'versions': [1]},
    'Resources': {'versions': [1, 2, 3]},
    'ResourcesHookContext': {'versions': [1]},
    'Resumer': {'versions': [2]},
    'RetryStrategy': {'versions': [1]},
    'Secrets': {'versions': [1, 2]},
    'SecretsManager': {'versions': [1, 2]},
    'SecretBackends': {'versions': [1]},
    'SecretBackendsManager': {'versions': [1]},
    'SecretBackendsRotateWatcher': {'versions': [1]},
    'SecretsDrain': {'versions': [1]},
    'SecretsRevisionWatcher': {'versions': [1]},
    'SecretsRotationWatcher': {'versions': [1]},
    'SecretsTriggerWatcher': {'versions': [1]},
    'Singular': {'versions': [2]},
    'Spaces': {'versions': [6]},
    'StatusHistory': {'versions': [2]},
    'Storage': {'versions': [3, 4, 6]},
    'StorageProvisioner': {'versions': [3, 4]},
    'StringsWatcher': {'versions': [1]},
    'Subnets': {'versions': [2, 4, 5]},
    'SSHClient': {'versions': [1, 2, 3, 4]},
    'Undertaker': {'versions': [1]},
    'UnitAssigner': {'versions': [1]},
    'Uniter': {'versions': [18]},
    'Upgrader': {'versions': [1]},
    'UpgradeSeries': {'versions': [1, 3]},
    'UpgradeSteps': {'versions': [1, 2]},
    'UserManager': {'versions': [1, 2, 3]},
    'UserSecretsDrain': {'versions': [1]},
    'UserSecretsManager': {'versions': [1]},
    'VolumeAttachmentsWatcher': {'versions': [2]},
    'VolumeAttachmentPlansWatcher': {'versions': [1]},
}


def facade_versions(name, versions):
    """
    facade_versions returns a new object that correctly returns a object in
    format expected by the connection facades inspection.
    :param name: name of the facade
    :param versions: versions to support by the facade
    """
    if name.endswith('Facade'):
        name = name[:-len('Facade')]
    return {
        name: {'versions': versions},
    }


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
        self.reconnecting = jasyncio.Lock()
        self.close_called = jasyncio.Event()

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
        if not connection._ws:
            return self.DISCONNECTED

        # close called but not yet complete
        if self.close_called.is_set():
            return self.DISCONNECTING

        # connection closed uncleanly (we didn't call connection.close)
        if connection.is_debug_log_connection:
            stopped = connection._debug_log_task.cancelled()
        else:
            stopped = connection._receiver_task is not None and connection._receiver_task.cancelled()

        if stopped or not connection._ws.open:
            return self.ERROR

        # everything is fine!
        return self.CONNECTED


class Connection:
    """
    Usage::

        # Connect to an arbitrary api server
        client = await Connection.connect(
            api_endpoint, model_uuid, username, password, cacert)

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
            max_frame_size=None,
            retries=3,
            retry_backoff=10,
            specified_facades=None,
            proxy=None,
            debug_log_conn=None,
            debug_log_params={}
    ):
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
        :param specified_facades: Define a series of facade versions you wish to override
            to prevent using the conservative client pinning with in the client.
        :param TextIOWrapper debug_log_conn: target if this is a debug log connection
        :param dict debug_log_params: filtering parameters for the debug-log output
        """
        self = cls()
        if endpoint is None:
            raise ValueError('no endpoint provided')
        if not isinstance(endpoint, str) and not isinstance(endpoint, list):
            raise TypeError("Endpoint should be either str or list")
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
        self.specified_facades = specified_facades or {}

        self.messages = IdQueue()
        self.monitor = Monitor(connection=self)
        if max_frame_size is None:
            max_frame_size = self.MAX_FRAME_SIZE
        self.max_frame_size = max_frame_size

        self.proxy = proxy
        if self.proxy is not None:
            self.proxy.connect()

        _endpoints = [(endpoint, cacert)] if isinstance(endpoint, str) else [(e, cacert) for e in endpoint]
        lastError = None
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
                lastError = e
                continue
            except OSError as e:
                logging.debug(
                    "Cannot access endpoint {}: {}".format(_ep, e.strerror))
                lastError = e
                continue
        if lastError is not None:
            raise lastError
        raise Exception("Unable to connect to websocket")

    @property
    def ws(self):
        log.warning('Direct access to the websocket object may cause disruptions in asyncio event handling.')
        return self._ws

    @property
    def username(self):
        if not self.usertag:
            return None
        return self.usertag[len('user-'):]

    @property
    def is_using_old_client(self):
        if self.info is None:
            raise errors.JujuError("Not connected yet.")
        return self.info['server-version'].startswith('2.')

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

        if self.is_debug_log_connection:
            assert self.uuid
            url = "wss://user-{}:{}@{}/model/{}/log".format(
                self.username, self.password, endpoint, self.uuid)
        elif self.uuid:
            url = "wss://{}/model/{}/api".format(endpoint, self.uuid)
        else:
            url = "wss://{}/api".format(endpoint)

        # We need to establish a server_hostname here for TLS sni if we are
        # connecting through a proxy as the Juju controller certificates will
        # not be covering the proxy
        sock = None
        server_hostname = None
        if self.proxy is not None:
            sock = self.proxy.socket()
            server_hostname = "juju-app"

        def _exit_tasks():
            for task in jasyncio.all_tasks():
                task.cancel()

        loop = jasyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _exit_tasks)

        return (await websockets.connect(
            url,
            ssl=self._get_ssl(cacert),
            max_size=self.max_frame_size,
            server_hostname=server_hostname,
            sock=sock,
        )), url, endpoint, cacert

    async def close(self, to_reconnect=False):
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

        if self._ws and not self._ws.closed:
            await self._ws.close()

        if not to_reconnect:
            try:
                log.debug('Gathering all tasks for connection close')
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

        # Remove signal handlers
        loop = jasyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.remove_signal_handler(sig)

    async def _recv(self, request_id):
        if not self.is_open:
            raise websockets.exceptions.ConnectionClosed(0, 'websocket closed')
        try:
            return await self.messages.get(request_id)
        except GeneratorExit:
            return {}

    def debug_log_filter_write(self, result):

        write_or_not = True

        entity = result['tag']
        msg_lev = result['sev']
        mod = result['mod']
        msg = result['msg']

        excluded_entities = self.debug_log_params['exclude']
        excluded_modules = self.debug_log_params['exclude_module']
        write_or_not = write_or_not and \
            (mod not in excluded_modules) and \
            (entity not in excluded_entities)

        included_entities = self.debug_log_params['include']
        only_these_modules = self.debug_log_params['include_module']
        write_or_not = write_or_not and \
            (only_these_modules == [] or mod in only_these_modules) and \
            (included_entities == [] or entity in included_entities)

        LEVELS = ['TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR']
        log_level = self.debug_log_params['level']

        if log_level != "" and log_level not in LEVELS:
            log.warning("Debug Logger: level should be one of %s, given %s" % (LEVELS, log_level))
        else:
            write_or_not = write_or_not and \
                (log_level == "" or (LEVELS.index(msg_lev) >= LEVELS.index(log_level)))

        # TODO
        # lines = self.debug_log_params['lines']
        # no_tail = self.debug_log_params['no_tail']

        if write_or_not:
            ts = parse(result['ts'])

            self.debug_log_target.write("%s %02d:%02d:%02d %s %s %s\n" % (entity, ts.hour, ts.minute, ts.second, msg_lev, mod, msg))
            return 1
        else:
            return 0

    async def _debug_logger(self):
        try:
            while self.is_open:
                result = await utils.run_with_interrupt(
                    self._ws.recv(),
                    self.monitor.close_called,
                    log=log)
                if self.monitor.close_called.is_set():
                    break
                if result is not None and result != '{}\n':
                    result = json.loads(result)

                    number_of_lines_written = self.debug_log_filter_write(result)

                    self.debug_log_shown_lines += number_of_lines_written

                    if self.debug_log_shown_lines >= self.debug_log_params['limit']:
                        jasyncio.create_task(self.close(), name="Task_Close")
                        return

        except KeyError as e:
            log.exception('Unexpected debug line -- %s' % e)
            jasyncio.create_task(self.close(), name="Task_Close")
            raise
        except jasyncio.CancelledError:
            jasyncio.create_task(self.close(), name="Task_Close")
            raise
        except websockets.exceptions.ConnectionClosed:
            log.warning('Debug Logger: Connection closed, reconnecting')
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
                    self._ws.recv(),
                    self.monitor.close_called,
                    log=log)
                if self.monitor.close_called.is_set():
                    break
                if result is not None:
                    result = json.loads(result)
                    await self.messages.put(result['request-id'], result)
        except jasyncio.CancelledError:
            log.debug('Receiver: Cancelled')
            pass
        except websockets.exceptions.ConnectionClosed as e:
            log.warning('Receiver: Connection closed, reconnecting')
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
        '''
        A Controller can time us out if we are silent for too long. This
        is especially true in JaaS, which has a fairly strict timeout.

        To prevent timing out, we send a ping every ten seconds.

        '''
        async def _do_ping():
            try:
                log.debug(f'Pinger {self._pinger_task}: pinging')
                await pinger_facade.Ping()
            except jasyncio.CancelledError:
                raise

        pinger_facade = client.PingerFacade.from_connection(self)
        try:
            while True:
                await utils.run_with_interrupt(
                    _do_ping(),
                    self.monitor.close_called,
                    log=log)
                if self.monitor.close_called.is_set():
                    break
                await jasyncio.sleep(10)
        except jasyncio.CancelledError:
            log.debug('Pinger: Cancelled')
            pass
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
        if 'params' not in msg:
            msg['params'] = {}
        if "version" not in msg:
            msg['version'] = self.facades[msg['type']]
        outgoing = json.dumps(msg, indent=2, cls=encoder)
        log.debug('connection id: {} ---> {}'.format(id(self), outgoing))
        for attempt in range(3):
            if self.monitor.status == Monitor.DISCONNECTED:
                # closed cleanly; shouldn't try to reconnect
                raise websockets.exceptions.ConnectionClosed(
                    0, 'websocket closed')
            try:
                await self._ws.send(outgoing)
                break
            except websockets.ConnectionClosed:
                if attempt == 2:
                    raise
                log.warning('RPC: Connection closed, reconnecting')
                # the reconnect has to be done in a separate task because,
                # if it is triggered by the pinger, then this RPC call will
                # be cancelled when the pinger is cancelled by the reconnect,
                # and we don't want the reconnect to be aborted halfway through
                await jasyncio.wait([self.reconnect()])
                if self.monitor.status != Monitor.CONNECTED:
                    # reconnect failed; abort and shutdown
                    log.error('RPC: Automatic reconnect failed')
                    raise
        result = await self._recv(msg['request-id'])
        log.debug('connection id : {} <--- {}'.format(id(self), result))

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
            for res in result['response']['results'] or []:
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
        # Support IPv6 by right splitting on : and removing [] around IP address for host
        host, remainder = endpoint.rsplit(':', 1)
        host = host.strip("[]")
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
        """Return a dict of parameters suitable for passing to
        Connection.connect that can be used to make a new connection
        to the same controller (and model if specified).
        """
        return {
            'endpoint': self.endpoint,
            'uuid': self.uuid,
            'username': self.username,
            'password': self.password,
            'cacert': self.cacert,
            'bakery_client': self.bakery_client,
            'max_frame_size': self.max_frame_size,
            'proxy': self.proxy,
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
            max_frame_size=self.max_frame_size,
        )

    async def reconnect(self):
        """ Force a reconnection.
        """
        monitor = self.monitor
        if monitor.reconnecting.locked() or monitor.close_called.is_set():
            return
        async with monitor.reconnecting:
            await self.close(to_reconnect=True)
            connector = self._connect if self.is_debug_log_connection else self._connect_with_login
            res = await connector(
                [(self.endpoint, self.cacert)]
                if not self.endpoints else
                self.endpoints
            )
            if not self.is_debug_log_connection:
                self._build_facades(res.get('facades', {}))
                if not self._pinger_task:
                    log.debug('reconnect: scheduling a pinger task')
                    self._pinger_task = jasyncio.create_task(self._pinger(), name="Task_Pinger")

    async def _connect(self, endpoints):
        if len(endpoints) == 0:
            raise errors.JujuConnectionError('no endpoints to connect to')

        async def _try_endpoint(endpoint, cacert, delay):
            if delay:
                await jasyncio.sleep(delay)
            return await self._open(endpoint, cacert)

        # Try all endpoints in parallel, with slight increasing delay (+100ms
        # for each subsequent endpoint); the delay allows us to prefer the
        # earlier endpoints over the latter. Use first successful connection.
        tasks = [jasyncio.ensure_future(_try_endpoint(endpoint, cacert,
                                                      0.1 * i))
                 for i, (endpoint, cacert) in enumerate(endpoints)]
        for attempt in range(self._retries + 1):
            for task in jasyncio.as_completed(tasks):
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
                    await jasyncio.sleep((attempt + 1) * self._retry_backoff)
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
        self._ws = result[0]
        self.addr = result[1]
        self.endpoint = result[2]
        self.cacert = result[3]

        #  If this is a debug-log connection, and the _debug_log_task
        #  is not created yet, then go ahead and schedule it
        if self.is_debug_log_connection and not self._debug_log_task:
            self._debug_log_task = jasyncio.create_task(self._debug_logger(), name="Task_Debug_Log")

        #  If this is regular connection, and we dont have a
        #  receiver_task yet, then schedule a _receiver_task
        elif not self.is_debug_log_connection and not self._receiver_task:
            log.debug('_connect: scheduling a receiver task')
            self._receiver_task = jasyncio.create_task(self._receiver(), name="Task_Receiver")

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
        if not self._pinger_task:
            log.debug('_connect_with_redirect: scheduling a pinger task')
            self._pinger_task = jasyncio.create_task(self._pinger(), name="Task_Pinger")

    # _build_facades takes the facade list that comes from the connection with the controller,
    # validates that the client knows about them (client_facades) and builds the facade list
    # (into the self.specified facades) with the max versions that both the client and the controller
    # can negotiate on
    def _build_facades(self, facades_from_connection):
        self.facades.clear()
        for facade in facades_from_connection:
            name = facade['name']
            # the following attempts to get the best facade version for the
            # client. The client knows about the best facade versions it speaks,
            # so in order to be compatible forwards and backwards we speak a
            # common facade versions.
            if (name not in client_facades) and (name not in self.specified_facades):
                # if a facade is required but the client doesn't know about
                # it, then log a warning.
                log.warning(f'unexpected facade {name} received from the controller')
                continue

            try:
                # allow the ability to specify a set of facade versions, so the
                # client can define the non-conservative facade client pinning.
                if name in self.specified_facades:
                    client_versions = self.specified_facades[name]['versions']
                elif name in client_facades:
                    client_versions = client_facades[name]['versions']

                controller_versions = facade['versions']
                # select the max version that both the client and the controller know
                version = max(set(client_versions).intersection(set(controller_versions)))
            except ValueError:
                # this can occur if client_verisons is [1, 2] and controller_versions is [3, 4]
                # there is just no way to know how to communicate with the facades we're trying to call.
                log.warning(f'unknown common facade version for {name},\n'
                            f'versions known to client : {client_versions}\n'
                            f'versions known to controller : {controller_versions}')
            except errors.JujuConnectionError:
                # If the facade isn't with in the local facades then it's not
                # possible to reason about what version should be used. In this
                # case we should log the facade was found, but we couldn't
                # handle it.
                log.warning(f'unexpected facade {name} found, unable to determine which version to use')
            else:
                self.facades[name] = version

    async def login(self):
        params = {}
        # Set the client version
        params['client-version'] = TARGET_JUJU_VERSION
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


def _macaroons_for_domain(cookies, domain):
    '''Return any macaroons from the given cookie jar that
    apply to the given domain name.'''
    req = urllib.request.Request('https://' + domain + '/')
    cookies.add_cookie_header(req)
    return httpbakery.extract_macaroons(req)
