import copy
import logging

import macaroonbakery.httpbakery as httpbakery
from juju.client.connection import Connection
from juju.client.gocookies import GoCookieJar, go_to_py_cookie
from juju.client.jujudata import FileJujuData
from juju.client.proxy.factory import proxy_from_config
from juju.errors import JujuConnectionError, JujuError
from juju.client import client

log = logging.getLogger('connector')


class NoConnectionException(Exception):
    '''Raised by Connector when the connection method is called
    and there is no current connection.'''
    pass


class Connector:
    '''This class abstracts out a reconnectable client that can connect
    to controllers and models found in the Juju data files.
    '''
    def __init__(
        self,
        max_frame_size=None,
        bakery_client=None,
        jujudata=None,
    ):
        '''Initialize a connector that will use the given parameters
        by default when making a new connection'''
        self.max_frame_size = max_frame_size
        self.bakery_client = bakery_client
        self._connection = None
        self._log_connection = None
        self.controller_name = None
        self.controller_uuid = None
        self.model_name = None
        self.jujudata = jujudata or FileJujuData()

    def is_connected(self):
        '''Report whether there is a currently connected controller or not'''
        return self._connection is not None

    def connection(self):
        '''Return the current connection; raises an exception if there
        is no current connection.'''
        if not self.is_connected():
            raise NoConnectionException('not connected')
        return self._connection

    async def connect(self, **kwargs):
        """Connect to an arbitrary Juju model.

        kwargs are passed through to Connection.connect()
        """
        kwargs.setdefault('max_frame_size', self.max_frame_size)
        kwargs.setdefault('bakery_client', self.bakery_client)
        if 'macaroons' in kwargs:
            if not kwargs['bakery_client']:
                kwargs['bakery_client'] = httpbakery.Client()
            if not kwargs['bakery_client'].cookies:
                kwargs['bakery_client'].cookies = GoCookieJar()
            jar = kwargs['bakery_client'].cookies
            for macaroon in kwargs.pop('macaroons'):
                jar.set_cookie(go_to_py_cookie(macaroon))
        if 'debug_log_conn' in kwargs:
            assert self._connection
            self._log_connection = await Connection.connect(**kwargs)
        else:
            if self._connection:
                await self._connection.close()
            self._connection = await Connection.connect(**kwargs)

    async def disconnect(self):
        """Shut down the watcher task and close websockets.
        """
        if self._connection:
            log.debug('Closing model connection')
            await self._connection.close()
            self._connection = None
        if self._log_connection:
            log.debug('Also closing debug-log connection')
            await self._log_connection.close()
            self._log_connection = None

    async def connect_controller(self, controller_name=None, specified_facades=None):
        """Connect to a controller by name. If the name is empty, it
        connect to the current controller.
        """
        if not controller_name:
            controller_name = self.jujudata.current_controller()
        if not controller_name:
            raise JujuConnectionError('No current controller')

        controller = self.jujudata.controllers()[controller_name]
        endpoints = controller['api-endpoints']
        accounts = self.jujudata.accounts().get(controller_name, {})

        proxy = proxy_from_config(controller.get('proxy-config', None))

        await self.connect(
            endpoint=endpoints,
            uuid=None,
            username=accounts.get('user'),
            password=accounts.get('password'),
            cacert=controller.get('ca-cert'),
            bakery_client=self.bakery_client_for_controller(controller_name),
            specified_facades=specified_facades,
            proxy=proxy,
        )
        self.controller_name = controller_name
        self.controller_uuid = controller["uuid"]

    async def connect_model(self, _model_name=None, **kwargs):
        """Connect to a model by name. If either controller or model
        parts of the name are empty, the current controller and/or model
        will be used.

        :param str model: <controller>:<model>
        """

        try:
            controller_name, _model_name = self.jujudata.parse_model(_model_name)
            controller = self.jujudata.controllers().get(controller_name)
        except JujuError as e:
            raise JujuConnectionError(e.message) from e
        if controller is None:
            raise JujuConnectionError('Controller {} not found'.format(
                controller_name))
        endpoints = controller['api-endpoints']
        account = self.jujudata.accounts().get(controller_name, {})
        models = self.jujudata.models().get(controller_name, {}).get('models',
                                                                     {})
        model_uuid = None
        if _model_name in models:
            model_uuid = models[_model_name]['uuid']
        else:
            # let's try to find it through the actual controller
            await self.connect_controller(controller_name=controller_name)
            # get the facade
            controller_facade = client.ControllerFacade.from_connection(
                self.connection())
            # get all the user models from the api
            response = await controller_facade.AllModels()
            # search the one that contains admin/model_name
            for user_model in response.user_models:
                if 'admin/' + user_model.model.name == _model_name:
                    model_uuid = user_model.model.uuid

        if model_uuid is None:
            raise JujuConnectionError('Model not found: {}'.format(_model_name))

        proxy = proxy_from_config(controller.get('proxy-config', None))

        # TODO remove the need for base.CleanModel to subclass
        # JujuData.
        kwargs.update(endpoint=endpoints,
                      uuid=model_uuid,
                      username=account.get('user'),
                      password=account.get('password'),
                      cacert=controller.get('ca-cert'),
                      bakery_client=self.bakery_client_for_controller(controller_name),
                      proxy=proxy)
        await self.connect(**kwargs)
        # TODO this might be a good spot to trigger refreshing the
        # local cache (the connection to the model might help)
        self.controller_name = controller_name
        self.model_name = controller_name + ':' + _model_name
        return self.controller_name, model_uuid

    def bakery_client_for_controller(self, controller_name):
        '''Make a copy of the bakery client with a the appropriate controller's
        cookiejar in it.
        '''
        bakery_client = self.bakery_client
        if bakery_client:
            bakery_client = copy.copy(bakery_client)
        else:
            bakery_client = httpbakery.Client()
        bakery_client.cookies = self.jujudata.cookies_for_controller(
            controller_name)
        return bakery_client
