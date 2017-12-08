import asyncio
import logging

import macaroonbakery.httpbakery as httpbakery
from juju.client.connection import Connection
from juju.client.jujudata import JujuData
from juju.errors import JujuConnectionError, JujuError

log = logging.getLogger('connector')


class NoConnectionException(Exception):
    '''Raised by Connector when the connection method is called
    and there is no current connection.'''
    pass


class Connector:
    '''This class abstracts out a reconnectable client that can connect
    to controllers and models found in the Juju data files.
    '''
    def __init__(self, loop=None, max_frame_size=None, bakery_client=None):
        '''Initialize a connector that will use the given parameters
        by default when making a new connection'''
        self.max_frame_size = max_frame_size
        self.loop = loop or asyncio.get_event_loop()
        self.bakery_client = bakery_client
        self._connection = None
        self.controller_name = None
        self.model_name = None
        self.jujudata = JujuData()

    def is_connected(self):
        '''Report whether there is a currently connected controller or not'''
        return self._connection is not None

    def connection(self):
        '''Return the current connection; raises an exception if there
        is no current connection.'''
        if not self.is_connected():
            raise NoConnectionException('not connected')
        return self._connection

    async def connect(self, *args, **kw):
        """Connect to an arbitrary Juju model.

        args and kw are passed through to Connection.connect()
        """
        kw.setdefault('loop', self.loop)
        kw.setdefault('max_frame_size', self.max_frame_size)
        kw.setdefault('bakery_client', self.bakery_client)
        self._connection = await Connection.connect(*args, **kw)

    async def disconnect(self):
        """Shut down the watcher task and close websockets.
        """
        if self._connection:
            log.debug('Closing model connection')
            await self._connection.close()
            self._connection = None

    async def connect_controller(self, controller_name=None):
        """Connect to a controller by name. If the name is empty, it
        connect to the current controller.
        """
        if not controller_name:
            controller_name = self.jujudata.current_controller()
        if not controller_name:
            raise JujuConnectionError('No current controller')

        controller = self.jujudata.controllers()[controller_name]
        # TODO change Connection so we can pass all the endpoints
        # instead of just the first.
        endpoint = controller['api-endpoints'][0]
        accounts = self.jujudata.accounts()[controller_name]

        await self.connect(
            endpoint=endpoint,
            uuid=None,
            username=accounts.get('user'),
            password=accounts.get('password'),
            cacert=controller.get('ca-cert'),
            bakery_client=self.bakery_client_for_controller(controller_name),
        )
        self.controller_name = controller_name

    async def connect_model(self, model_name=None):
        """Connect to a model by name. If either controller or model
        parts of the name are empty, the current controller and/or model
        will be used.

        :param str model: <controller>:<model>
        """

        try:
            controller_name, model_name = self.jujudata.parse_model(model_name)
            controller = self.jujudata.controllers().get(controller_name)
        except JujuError as e:
            raise JujuConnectionError(e.message) from e
        if controller is None:
            raise JujuConnectionError('Controller {} not found'.format(controller_name))
        # TODO change Connection so we can pass all the endpoints
        # instead of just the first one.
        endpoint = controller['api-endpoints'][0]
        models = self.jujudata.models()[controller_name]
        account = self.jujudata.accounts()[controller_name]

        # TODO if there's no record for the required model name, connect
        # to the controller to find out the model's uuid, then connect
        # to that. This will let connect_model work with models that
        # haven't necessarily synced with the local juju data,
        # and also remove the need for base.CleanModel to
        # patch JujuData.models with a mock.
        await self.connect(
            endpoint=endpoint,
            uuid=models['models'][model_name]['uuid'],
            username=account.get('user'),
            password=account.get('password'),
            cacert=controller.get('ca-cert'),
            bakery_client=self.bakery_client_for_controller(controller_name),
        )
        self.controller_name = controller_name
        self.model_name = controller_name + ':' + model_name

    def bakery_client_for_controller(self, controller_name):
        '''Make a copy of the bakery client with a the appropriate controller's
        cookiejar in it.
        '''
        bakery_client = self.bakery_client
        if bakery_client:
            bakery_client = bakery_client.clone()
        else:
            bakery_client = httpbakery.Client()
        bakery_client.cookies = self.jujudata.cookies_for_controller(controller_name)
