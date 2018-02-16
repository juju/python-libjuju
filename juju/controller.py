import asyncio
import logging

from . import errors, tag, utils
from .client import client, connector
from .user import User

log = logging.getLogger(__name__)


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
        :param jujudata JujuData: The source for current controller information.
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

    async def connect(self, controller_name=None, **kwargs):
        """Connect to a Juju controller.

        If any arguments are specified other than controller_name,
        then controller_name must be None and an explicit
        connection will be made using Connection.connect
        using those parameters (the 'uuid' parameter must
        be absent or None).

        Otherwise, if controller_name is None, connect to the
        current controller.

        Otherwise, controller_name must specify the name
        of a known controller.
        """
        await self.disconnect()
        if not kwargs:
            await self._connector.connect_controller(controller_name)
        else:
            if controller_name is not None:
                raise ValueError('controller name may not be specified with other connect parameters')
            if kwargs.get('uuid') is not None:
                # A UUID implies a model connection, not a controller connection.
                raise ValueError('model UUID specified when connecting to controller')
            await self._connector.connect(**kwargs)

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

    async def disconnect(self):
        """Shut down the watcher task and close websockets.

        """
        await self._connector.disconnect()

    async def add_credential(self, name=None, credential=None, cloud=None,
                             owner=None):
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
        :returns: Name of credential that was uploaded.
        """
        if not cloud:
            cloud = await self.get_cloud()

        if not owner:
            owner = self.connection().info['user-info']['identity']

        if credential and not name:
            raise errors.JujuError('Name must be provided for credential')

        if not credential:
            name, credential = self._connector.jujudata.load_credential(cloud, name)
            if credential is None:
                raise errors.JujuError(
                    'Unable to find credential: {}'.format(name))

        log.debug('Uploading credential %s', name)
        cloud_facade = client.CloudFacade.from_connection(self.connection())
        await cloud_facade.UpdateCredentials([
            client.UpdateCloudCredential(
                tag=tag.credential(cloud, tag.untag('user-', owner), name),
                credential=credential,
            )])

        return name

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
            tag.cloud(cloud_name),
            config,
            credential,
            model_name,
            owner,
            region
        )
        from juju.model import Model
        model = Model(jujudata=self._connector.jujudata)
        kwargs = self.connection().connect_params()
        kwargs['uuid'] = model_info.uuid
        await model._connect_direct(**kwargs)

        return model

    async def destroy_models(self, *models):
        """Destroy one or more models.

        :param str \*models: Names or UUIDs of models to destroy

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

        await model_facade.DestroyModels([
            client.Entity(tag.model(model))
            for model in models
        ])
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
        user_facade = client.UserManagerFacade.from_connection(self.connection())
        users = [client.AddUser(display_name=display_name,
                                username=username,
                                password=password)]
        await user_facade.AddUser(users)
        return await self.get_user(username)

    async def remove_user(self, username):
        """Remove a user from this controller.
        """
        client_facade = client.UserManagerFacade.from_connection(
            self.connection())
        user = tag.user(username)
        await client_facade.RemoveUser([client.Entity(user)])

    async def change_user_password(self, username, password):
        """Change the password for a user in this controller.

        :param str username: Username
        :param str password: New password

        """
        user_facade = client.UserManagerFacade.from_connection(self.connection())
        entity = client.EntityPassword(password, tag.user(username))
        return await user_facade.SetPassword([entity])

    async def destroy(self, destroy_all_models=False):
        """Destroy this controller.

        :param bool destroy_all_models: Destroy all hosted models in the
            controller.

        """
        controller_facade = client.ControllerFacade.from_connection(
            self.connection())
        return await controller_facade.DestroyController(destroy_all_models)

    async def disable_user(self, username):
        """Disable a user.

        :param str username: Username

        """
        user_facade = client.UserManagerFacade.from_connection(self.connection())
        entity = client.Entity(tag.user(username))
        return await user_facade.DisableUser([entity])

    async def enable_user(self, username):
        """Re-enable a previously disabled user.

        """
        user_facade = client.UserManagerFacade.from_connection(self.connection())
        entity = client.Entity(tag.user(username))
        return await user_facade.EnableUser([entity])

    def kill(self):
        """Forcibly terminate all machines and other associated resources for
        this controller.

        """
        raise NotImplementedError()

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
            self.connection)
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

        :param str \*patterns: Patterns to match against

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

    async def get_user(self, username):
        """Get a user by name.

        :param str username: Username
        :returns: A :class:`~juju.user.User` instance
        """
        client_facade = client.UserManagerFacade.from_connection(
            self.connection())
        user = tag.user(username)
        args = [client.Entity(user)]
        try:
            response = await client_facade.UserInfo(args, True)
        except errors.JujuError as e:
            if 'permission denied' in e.errors:
                # apparently, trying to get info for a nonexistent user returns
                # a "permission denied" error rather than an empty result set
                return None
            raise
        if response.results and response.results[0].result:
            return User(self, response.results[0].result)
        return None

    async def get_users(self, include_disabled=False):
        """Return list of users that can connect to this controller.

        :param bool include_disabled: Include disabled users
        :returns: A list of :class:`~juju.user.User` instances
        """
        client_facade = client.UserManagerFacade.from_connection(
            self.connection())
        response = await client_facade.UserInfo(None, include_disabled)
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
            await controller_facade.ModifyControllerAccess([changes])
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
        return await controller_facade.ModifyControllerAccess([changes])

    async def grant_model(self, username, model_uuid, acl='read'):
        """Grant a user access to a model. Note that if the user
        already has higher permissions than the provided ACL,
        this will do nothing (see revoke_model for a way to remove permissions).

        :param str username: Username
        :param str model_uuid: The UUID of the model to change.
        :param str acl: Access control ('read, 'write' or 'admin')
        """
        model_facade = client.ModelManagerFacade.from_connection(
            self.connection())
        user = tag.user(username)
        model = tag.model(model_uuid)
        changes = client.ModifyModelAccess(acl, 'grant', model, user)
        return await model_facade.ModifyModelAccess([changes])

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
        model = tag.model(self.info.uuid)
        changes = client.ModifyModelAccess(acl, 'revoke', model, user)
        return await model_facade.ModifyModelAccess([changes])
