import asyncio
import json
import logging
from concurrent.futures import CancelledError
from pathlib import Path

import websockets

from . import errors, tag, utils
from .client import client, connector
from .errors import JujuAPIError
from .offerendpoints import ParseError as OfferParseError
from .offerendpoints import parse_offer_endpoint, parse_offer_url
from .user import User

log = logging.getLogger(__name__)


class RemoveError(Exception):
    def __init__(self, message):
        self.message = message


class Controller:
    def __init__(
        self,
        loop=None,
        max_frame_size=None,
        bakery_client=None,
        jujudata=None,
    ):
        """Instantiate a new Controller.

        One of the connect_* methods will need to be called before this
        object can be used for anything interesting.

        If jujudata is None, jujudata.FileJujuData will be used.

        :param loop: an asyncio event loop
        :param max_frame_size: See
            `juju.client.connection.Connection.MAX_FRAME_SIZE`
        :param bakery_client httpbakery.Client: The bakery client to use
            for macaroon authorization.
        :param jujudata JujuData: The source for current controller
        information.
        """
        self._connector = connector.Connector(
            loop=loop,
            max_frame_size=max_frame_size,
            bakery_client=bakery_client,
            jujudata=jujudata,
        )

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    @property
    def loop(self):
        return self._connector.loop

    async def connect(self, *args, **kwargs):
        """Connect to a Juju controller.

        This supports two calling conventions:

        The controller and (optionally) authentication information can be
        taken from the data files created by the Juju CLI.  This convention
        will be used if a ``controller_name`` is specified, or if the
        ``endpoint`` is not.

        Otherwise, both the ``endpoint`` and authentication information
        (``username`` and ``password``, or ``bakery_client`` and/or
        ``macaroons``) are required.

        If a single positional argument is given, it will be assumed to be
        the ``controller_name``.  Otherwise, the first positional argument,
        if any, must be the ``endpoint``.

        Available parameters are:

        :param str controller_name:  Name of controller registered with the
            Juju CLI.
        :param str endpoint: The hostname:port of the controller to connect to.
        :param str username: The username for controller-local users (or None
            to use macaroon-based login.)
        :param str password: The password for controller-local users.
        :param str cacert: The CA certificate of the controller
            (PEM formatted).
        :param httpbakery.Client bakery_client: The macaroon bakery client to
            to use when performing macaroon-based login. Macaroon tokens
            acquired when logging will be saved to bakery_client.cookies.
            If this is None, a default bakery_client will be used.
        :param list macaroons: List of macaroons to load into the
            ``bakery_client``.
        :param asyncio.BaseEventLoop loop: The event loop to use for async
            operations.
        :param int max_frame_size: The maximum websocket frame size to allow.
        :param specified_facades: Overwrite the facades with a series of
            specified facades.
        """
        await self.disconnect()
        if 'endpoint' not in kwargs and len(args) < 2:
            if args and 'model_name' in kwargs:
                raise TypeError('connect() got multiple values for '
                                'controller_name')
            elif args:
                controller_name = args[0]
            else:
                controller_name = kwargs.pop('controller_name', None)
            await self._connector.connect_controller(controller_name, **kwargs)
        else:
            if 'controller_name' in kwargs:
                raise TypeError('connect() got values for both '
                                'controller_name and endpoint')
            if args and 'endpoint' in kwargs:
                raise TypeError('connect() got multiple values for endpoint')
            has_userpass = (len(args) >= 3 or
                            {'username', 'password'}.issubset(kwargs))
            has_macaroons = (len(args) >= 5 or not
                             {'bakery_client', 'macaroons'}.isdisjoint(kwargs))
            if not (has_userpass or has_macaroons):
                raise TypeError('connect() missing auth params')
            arg_names = [
                'endpoint',
                'username',
                'password',
                'cacert',
                'bakery_client',
                'macaroons',
                'loop',
                'max_frame_size',
            ]
            for i, arg in enumerate(args):
                kwargs[arg_names[i]] = arg
            if 'endpoint' not in kwargs:
                raise ValueError('endpoint is required '
                                 'if controller_name not given')
            if not ({'username', 'password'}.issubset(kwargs) or
                    {'bakery_client', 'macaroons'}.intersection(kwargs)):
                raise ValueError('Authentication parameters are required '
                                 'if controller_name not given')
            await self._connector.connect(**kwargs)
        await self.update_endpoints()

    async def update_endpoints(self):
        info = await self.info()
        self._connector._connection.endpoints = [
            (e, info.results[0].cacert)
            for e in info.results[0].addresses
        ]

    async def connect_current(self):
        """
        .. deprecated:: 0.7.3
           Use :meth:`.connect()` instead.
        """
        return await self.connect()

    async def connect_controller(self, controller_name):
        """
        .. deprecated:: 0.7.3
           Use :meth:`.connect(controller_name)` instead.
        """
        return await self.connect(controller_name)

    async def _connect_direct(self, **kwargs):
        await self.disconnect()
        await self._connector.connect(**kwargs)

    def is_connected(self):
        """Reports whether the Controller is currently connected."""
        return self._connector.is_connected()

    def connection(self):
        """Return the current Connection object. It raises an exception
        if the Controller is disconnected"""
        return self._connector.connection()

    @property
    def controller_name(self):
        return self._connector.controller_name

    @property
    def controller_uuid(self):
        return self._connector.controller_uuid

    @property
    async def api_endpoints(self):
        """Get API endpoints

        :return list string: List of API Endpoints
        """
        info = await self.info()
        return info.results[0].addresses

    async def disconnect(self):
        """Shut down the watcher task and close websockets.

        """
        await self._connector.disconnect()

    async def add_credential(self, name=None, credential=None, cloud=None,
                             owner=None, force=False):
        """Add or update a credential to the controller.

        :param str name: Name of new credential. If None, the default
            local credential is used.  Name must be provided if a credential
            is given.
        :param CloudCredential credential: Credential to add. If not given,
            it will attempt to read from local data, if available.
        :param str cloud: Name of cloud to associate the credential with.
            Defaults to the same cloud as the controller.
        :param str owner: Username that will own the credential. Defaults to
            the current user.
        :param bool force: Force indicates whether the update should be forced.
            It's only supported for facade v3 or later.
            Defaults to false.
        :returns: Name of credential that was uploaded.
        """
        if not cloud:
            cloud = await self.get_cloud()

        if not owner:
            owner = self.connection().info['user-info']['identity']

        if credential and not name:
            raise errors.JujuError('Name must be provided for credential')

        if not credential:
            name, credential = self._connector.jujudata.load_credential(cloud,
                                                                        name)
            if credential is None:
                raise errors.JujuError(
                    'Unable to find credential: {}'.format(name))

        if credential.auth_type == 'jsonfile' and 'file' in credential.attrs:
            # file creds have to be loaded before being sent to the controller
            try:
                # it might already be JSON
                json.loads(credential.attrs['file'])
            except json.JSONDecodeError:
                # not valid JSON, so maybe it's a file
                cred_path = Path(credential.attrs['file'])
                if cred_path.exists():
                    # make a copy
                    cred_json = credential.to_json()
                    credential = client.CloudCredential.from_json(cred_json)
                    # inline the cred
                    credential.attrs['file'] = cred_path.read_text()

        log.debug('Uploading credential %s', name)
        cloud_facade = client.CloudFacade.from_connection(self.connection())
        tagged_credentials = [
            client.UpdateCloudCredential(
                tag=tag.credential(cloud, tag.untag('user-', owner), name),
                credential=credential,
            )]
        if cloud_facade.version >= 3:
            # UpdateCredentials was renamed to UpdateCredentialsCheckModels
            # in facade version 3.
            await cloud_facade.UpdateCredentialsCheckModels(
                credentials=tagged_credentials, force=force,
            )
        else:
            await cloud_facade.UpdateCredentials(credentials=tagged_credentials)
        return name

    async def add_cloud(self, name, cloud):
        """Add a cloud to this controller.

        :param str name: Name to give the new cloud.
        :param Cloud cloud: Cloud configuration.
        :return Cloud: Cloud that was created.
        """
        log.debug('Adding cloud %s', name)
        cloud_facade = client.CloudFacade.from_connection(self.connection())
        await cloud_facade.AddCloud(cloud=cloud, name=name)
        result = await self.cloud(name=name)
        return result.cloud

    async def info(self):
        """Show Controller Info from connection

        :return ControllerAPIInfoResult
        """
        log.debug('Getting information')
        uuids = await self.model_uuids()
        controller_facade = client.ControllerFacade.from_connection(self.connection())
        params = [client.Entity(tag.model(uuids["controller"]))]
        return await controller_facade.ControllerAPIInfoForModels(entities=params)

    async def remove_cloud(self, name):
        """Remove a cloud from this controller.

        :param str name: Name of the cloud to remove.
        """
        log.debug('Removing cloud %s', name)
        cloud_facade = client.CloudFacade.from_connection(self.connection())
        await cloud_facade.RemoveClouds(entities=[client.Entity(tag.cloud(name))])

    async def add_model(
            self, model_name, cloud_name=None, credential_name=None,
            owner=None, config=None, region=None):
        """Add a model to this controller.

        :param str model_name: Name to give the new model.
        :param str cloud_name: Name of the cloud in which to create the
            model, e.g. 'aws'. Defaults to same cloud as controller.
        :param str credential_name: Name of the credential to use when
            creating the model. If not given, it will attempt to find a
            default credential.
        :param str owner: Username that will own the model. Defaults to
            the current user.
        :param dict config: Model configuration.
        :param str region: Region in which to create the model.
        :return Model: A connection to the newly created model.
        """
        model_facade = client.ModelManagerFacade.from_connection(
            self.connection())

        owner = owner or self.connection().info['user-info']['identity']
        cloud_name = cloud_name or await self.get_cloud()

        try:
            # attempt to add/update the credential from local data if available
            credential_name = await self.add_credential(
                name=credential_name,
                cloud=cloud_name,
                owner=owner)
        except errors.JujuError:
            # if it's not available locally, assume it's on the controller
            pass

        if credential_name:
            credential = tag.credential(
                cloud_name,
                tag.untag('user-', owner),
                credential_name
            )
        else:
            credential = None

        log.debug('Creating model %s', model_name)

        if not config or 'authorized-keys' not in config:
            config = config or {}
            config['authorized-keys'] = await utils.read_ssh_key(
                loop=self._connector.loop)

        model_info = await model_facade.CreateModel(
            cloud_tag=tag.cloud(cloud_name),
            config=config,
            credential=credential,
            name=model_name,
            owner_tag=owner,
            region=region
        )
        from juju.model import Model
        model = Model(jujudata=self._connector.jujudata)
        kwargs = self.connection().connect_params()
        kwargs['uuid'] = model_info.uuid
        await model._connect_direct(**kwargs)

        return model

    async def destroy_models(self, *models, destroy_storage=False):
        """Destroy one or more models.

        :param str *models: Names or UUIDs of models to destroy
        :param bool destroy_storage: Whether or not to destroy storage when
            destroying the models. Defaults to false.

        """
        uuids = await self.model_uuids()
        models = [uuids[model] if model in uuids else model
                  for model in models]

        model_facade = client.ModelManagerFacade.from_connection(
            self.connection())

        log.debug(
            'Destroying model%s %s',
            '' if len(models) == 1 else 's',
            ', '.join(models)
        )

        if model_facade.version >= 5:
            params = [
                client.DestroyModelParams(model_tag=tag.model(model),
                                          destroy_storage=destroy_storage)
                for model in models]
        else:
            params = [client.Entity(tag.model(model)) for model in models]

        await model_facade.DestroyModels(entities=params)
    destroy_model = destroy_models

    async def add_user(self, username, password=None, display_name=None):
        """Add a user to this controller.

        :param str username: Username
        :param str password: Password
        :param str display_name: Display name
        :returns: A :class:`~juju.user.User` instance
        """
        if not display_name:
            display_name = username
        user_facade = client.UserManagerFacade.from_connection(
            self.connection())
        users = [client.AddUser(display_name=display_name,
                                username=username,
                                password=password)]
        results = await user_facade.AddUser(users=users)
        secret_key = results.results[0].secret_key
        return await self.get_user(username, secret_key=secret_key)

    async def remove_user(self, username):
        """Remove a user from this controller.
        """
        client_facade = client.UserManagerFacade.from_connection(
            self.connection())
        user = tag.user(username)
        await client_facade.RemoveUser(entities=[client.Entity(user)])

    async def change_user_password(self, username, password):
        """Change the password for a user in this controller.

        :param str username: Username
        :param str password: New password

        """
        user_facade = client.UserManagerFacade.from_connection(
            self.connection())
        entity = client.EntityPassword(password=password, tag=tag.user(username))
        return await user_facade.SetPassword(changes=[entity])

    async def reset_user_password(self, username):
        """Reset user password.

        :param str username: Username
        :returns: A :class:`~juju.user.User` instance
        """
        user_facade = client.UserManagerFacade.from_connection(
            self.connection())
        entity = client.Entity(tag.user(username))
        results = await user_facade.ResetPassword(entities=[entity])
        secret_key = results.results[0].secret_key
        return await self.get_user(username, secret_key=secret_key)

    async def destroy(self, destroy_all_models=False, destroy_storage=False):
        """Destroy this controller.

        :param bool destroy_all_models: Destroy all hosted models in the
            controller.
        :param bool destroy_storage: Destory all hosted storage in the
            controller.
        """
        controller_facade = client.ControllerFacade.from_connection(
            self.connection())
        return await controller_facade.DestroyController(destroy_models=destroy_all_models, destroy_storage=destroy_storage)

    async def disable_user(self, username):
        """Disable a user.

        :param str username: Username

        """
        user_facade = client.UserManagerFacade.from_connection(
            self.connection())
        entity = client.Entity(tag.user(username))
        return await user_facade.DisableUser(entities=[entity])

    async def enable_user(self, username):
        """Re-enable a previously disabled user.

        """
        user_facade = client.UserManagerFacade.from_connection(
            self.connection())
        entity = client.Entity(tag.user(username))
        return await user_facade.EnableUser(entities=[entity])

    def kill(self):
        """Forcibly terminate all machines and other associated resources for
        this controller.

        """
        raise NotImplementedError()

    async def cloud(self, name=None):
        """Get Cloud

        :param str name: Cloud name. If not specified, the cloud where
                         the controller lives on is returned.
        :returns: -> ~CloudResult
        """
        if name is None:
            name = await self.get_cloud()
        entity = client.Entity(tag.cloud(name))
        cloud_facade = client.CloudFacade.from_connection(self.connection())
        cloud = await cloud_facade.Cloud(entities=[entity])
        if len(cloud.results) == 0:
            log.error("No clouds found.")
            raise
        elif len(cloud.results) > 1:
            log.error("More than one cloud found.")
            raise
        return cloud.results[0]

    async def clouds(self):
        """Get all the clouds in the controller

        :returns: -> ~CloudsResult
        """
        cloud_facade = client.CloudFacade.from_connection(self.connection())
        return await cloud_facade.Clouds()

    async def get_cloud(self):
        """
        Get the name of the cloud that this controller lives on.
        """
        cloud_facade = client.CloudFacade.from_connection(self.connection())

        result = await cloud_facade.Clouds()
        cloud = list(result.clouds.keys())[0]  # only lives on one cloud
        return tag.untag('cloud-', cloud)

    async def get_models(self, all_=False, username=None):
        """
        .. deprecated:: 0.7.0
           Use :meth:`.list_models` instead.
        """
        controller_facade = client.ControllerFacade.from_connection(
            self.connection())
        for attempt in (1, 2, 3):
            try:
                return await controller_facade.AllModels()
            except errors.JujuAPIError as e:
                # retry concurrency error until resolved in Juju
                # see: https://bugs.launchpad.net/juju/+bug/1721786
                if 'has been removed' not in e.message or attempt == 3:
                    raise

    async def model_uuids(self):
        """Return a mapping of model names to UUIDs.
        """
        controller_facade = client.ControllerFacade.from_connection(
            self.connection())
        for attempt in (1, 2, 3):
            try:
                response = await controller_facade.AllModels()
                return {um.model.name: um.model.uuid
                        for um in response.user_models}
            except errors.JujuAPIError as e:
                # retry concurrency error until resolved in Juju
                # see: https://bugs.launchpad.net/juju/+bug/1721786
                if 'has been removed' not in e.message or attempt == 3:
                    raise
                await asyncio.sleep(attempt, loop=self._connector.loop)

    async def list_models(self):
        """Return list of names of the available models on this controller.

        Equivalent to ``sorted((await self.model_uuids()).keys())``
        """
        uuids = await self.model_uuids()
        return sorted(uuids.keys())

    def get_payloads(self, *patterns):
        """Return list of known payloads.

        :param str *patterns: Patterns to match against

        Each pattern will be checked against the following info in Juju::

            - unit name
            - machine id
            - payload type
            - payload class
            - payload id
            - payload tag
            - payload status

        """
        raise NotImplementedError()

    def login(self):
        """Log in to this controller.

        """
        raise NotImplementedError()

    def logout(self, force=False):
        """Log out of this controller.

        :param bool force: Don't fail even if user not previously logged in
            with a password

        """
        raise NotImplementedError()

    async def get_model(self, model):
        """Get a model by name or UUID.

        :param str model: Model name or UUID
        :returns Model: Connected Model instance.
        """
        uuids = await self.model_uuids()
        if model in uuids:
            uuid = uuids[model]
        else:
            uuid = model

        from juju.model import Model
        model = Model()
        kwargs = self.connection().connect_params()
        kwargs['uuid'] = uuid
        await model._connect_direct(**kwargs)
        return model

    async def get_user(self, username, secret_key=None):
        """Get a user by name.

        :param str username: Username
        :param str secret_key: Issued by juju when add or reset user
            password
        :returns: A :class:`~juju.user.User` instance
        """
        client_facade = client.UserManagerFacade.from_connection(
            self.connection())
        user = tag.user(username)
        args = [client.Entity(user)]
        try:
            response = await client_facade.UserInfo(entities=args, include_disabled=True)
        except errors.JujuError as e:
            if 'permission denied' in e.errors:
                # apparently, trying to get info for a nonexistent user returns
                # a "permission denied" error rather than an empty result set
                return None
            raise
        if response.results and response.results[0].result:
            return User(self, response.results[0].result, secret_key=secret_key)
        return None

    async def get_users(self, include_disabled=False):
        """Return list of users that can connect to this controller.

        :param bool include_disabled: Include disabled users
        :returns: A list of :class:`~juju.user.User` instances
        """
        client_facade = client.UserManagerFacade.from_connection(
            self.connection())
        response = await client_facade.UserInfo(entities=None, include_disabled=include_disabled)
        return [User(self, r.result) for r in response.results]

    async def grant(self, username, acl='login'):
        """Grant access level of the given user on the controller.
        Note that if the user already has higher permissions than the
        provided ACL, this will do nothing (see revoke for a way to
        remove permissions).
        :param str username: Username
        :param str acl: Access control ('login', 'add-model' or 'superuser')
        :returns: True if new access was granted, False if user already had
            requested access or greater.  Raises JujuError if failed.
        """
        controller_facade = client.ControllerFacade.from_connection(
            self.connection())
        user = tag.user(username)
        changes = client.ModifyControllerAccess(acl, 'grant', user)
        try:
            await controller_facade.ModifyControllerAccess(changes=[changes])
            return True
        except errors.JujuError as e:
            if 'user already has' in str(e):
                return False
            else:
                raise

    async def revoke(self, username, acl='login'):
        """Removes some or all access of a user to from a controller
        If 'login' access is revoked, the user will no longer have any
        permissions on the controller. Revoking a higher privilege from
        a user without that privilege will have no effect.

        :param str username: username
        :param str acl: Access to remove ('login', 'add-model' or 'superuser')
        """
        controller_facade = client.ControllerFacade.from_connection(
            self.connection())
        user = tag.user(username)
        changes = client.ModifyControllerAccess('login', 'revoke', user)
        return await controller_facade.ModifyControllerAccess(changes=[changes])

    async def grant_model(self, username, model_uuid, acl='read'):
        """Grant a user access to a model. Note that if the user
        already has higher permissions than the provided ACL,
        this will do nothing (see revoke_model for a way to remove
        permissions).

        :param str username: Username
        :param str model_uuid: The UUID of the model to change.
        :param str acl: Access control ('read, 'write' or 'admin')
        """
        model_facade = client.ModelManagerFacade.from_connection(
            self.connection())
        user = tag.user(username)
        model = tag.model(model_uuid)
        changes = client.ModifyModelAccess(acl, 'grant', model, user)
        return await model_facade.ModifyModelAccess(changes=[changes])

    async def revoke_model(self, username, model_uuid, acl='read'):
        """Revoke some or all of a user's access to a model.
        If 'read' access is revoked, the user will no longer have any
        permissions on the model. Revoking a higher privilege from
        a user without that privilege will have no effect.

        :param str username: Username to revoke
        :param str model_uuid: The UUID of the model to change.
        :param str acl: Access control ('read, 'write' or 'admin')
        """
        model_facade = client.ModelManagerFacade.from_connection(
            self.connection())
        user = tag.user(username)
        model = tag.model(model_uuid)
        changes = client.ModifyModelAccess(acl, 'revoke', model, user)
        return await model_facade.ModifyModelAccess(changes=[changes])

    async def create_offer(self, model_uuid, endpoint, offer_name=None, application_name=None):
        """
        Offer a deployed application using a series of endpoints for use by
        consumers.

        @param endpoint: holds the application and endpoint you want to offer
        @param offer_name: over ride the offer name to help the consumer
        """
        try:
            offer = parse_offer_endpoint(endpoint)
        except OfferParseError as e:
            log.error(e.message)
            raise

        if offer_name is None:
            offer_name = offer.application

        if application_name is None:
            application_name = offer.application

        params = client.AddApplicationOffer()
        params.application_name = application_name
        params.endpoints = {name: name for name in offer.endpoints}
        params.offer_name = offer_name
        params.model_tag = tag.model(model_uuid)

        facade = client.ApplicationOffersFacade.from_connection(self.connection())
        return await facade.Offer(offers=[params])

    async def list_offers(self, model_name):
        """
        Offers list information about applications' endpoints that have been
        shared and who is connected.
        """
        params = client.OfferFilter()
        params.model_name = model_name

        facade = client.ApplicationOffersFacade.from_connection(self.connection())
        return await facade.ListApplicationOffers(filters=[params])

    async def remove_offer(self, model_uuid, offer, force=False):
        """
        Remove offer for an application.

        Offers will also remove relations to those offers, use force to do
        so, without an error.
        """
        url = None
        try:
            url = parse_offer_url(offer)
        except OfferParseError as e:
            log.error(e.message)
            raise
        if url is None:
            raise Exception

        offer_source = url.source
        if offer_source == "":
            offer_source = self.controller_name
        if not force:
            raise RemoveError("removing offer will also remove relations, use force and try again.")

        facade = client.ApplicationOffersFacade.from_connection(self.connection())
        return await facade.DestroyOffers(force=force, offer_urls=[url.string()])

    async def get_consume_details(self, endpoint):
        """
        get_consume_details returns the details necessary to pass to another
        model to consume the specified offers represented by the urls.
        """
        facade = client.ApplicationOffersFacade.from_connection(self.connection())
        offers = await facade.GetConsumeDetails(offer_urls=[endpoint])
        if len(offers.results) != 1:
            raise JujuAPIError("expected to find one result")
        result = offers.results[0]
        if result.error is not None:
            raise JujuAPIError(result.error)

        return result

    async def watch_model_summaries(self, callback, as_admin=False):
        """
        Watch the controller for model summary updates.

        If as_admin is true, a call will be made as the admin to watch
        all models in the controller. If the user isn't a superuser they
        will get a permission error.
        """
        stop_event = asyncio.Event(loop=self._connector.loop)

        async def _watcher(stop_event):
            try:
                facade = client.ControllerFacade.from_connection(
                    self.connection())
                watcher = client.ModelSummaryWatcherFacade.from_connection(
                    self.connection())
                if as_admin:
                    result = await facade.WatchAllModelSummaries()
                    watcher.Id = result.watcher_id
                else:
                    result = await facade.WatchModelSummaries()
                    log.debug("watcher id: {}".format(result.watcher_id))
                    watcher.Id = result.watcher_id

                while True:
                    try:
                        results = await utils.run_with_interrupt(
                            watcher.Next(),
                            stop_event,
                            loop=self._connector.loop)
                    except JujuAPIError as e:
                        if 'watcher was stopped' not in str(e):
                            raise
                    except websockets.ConnectionClosed:
                        break
                    if stop_event.is_set():
                        try:
                            await watcher.Stop()
                        except websockets.ConnectionClosed:
                            pass  # can't stop on a closed conn
                        break
                    for summary in results.models:
                        callback(summary)
            except CancelledError:
                pass
            except Exception:
                log.exception('Error in watcher')
                raise

        log.debug('Starting watcher task for model summaries')
        self._connector.loop.create_task(_watcher(stop_event))
        return stop_event
