import asyncio
import logging

from . import errors
from . import tag
from . import utils
from .client import client
from .client import connection
from .model import Model
from .user import User

log = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, loop=None,
                 max_frame_size=connection.Connection.DEFAULT_FRAME_SIZE):
        """Instantiate a new Controller.

        One of the connect_* methods will need to be called before this
        object can be used for anything interesting.

        :param loop: an asyncio event loop

        """
        self.loop = loop or asyncio.get_event_loop()
        self.max_frame_size = None
        self.connection = None
        self.controller_name = None

    async def connect(
            self, endpoint, username, password, cacert=None, macaroons=None):
        """Connect to an arbitrary Juju controller.

        """
        self.connection = await connection.Connection.connect(
            endpoint, None, username, password, cacert, macaroons,
            max_frame_size=self.max_frame_size)

    async def connect_current(self):
        """Connect to the current Juju controller.

        """
        jujudata = connection.JujuData()
        controller_name = jujudata.current_controller()
        if not controller_name:
            raise errors.JujuConnectionError('No current controller')
        return await self.connect_controller(controller_name)

    async def connect_controller(self, controller_name):
        """Connect to a Juju controller by name.

        """
        self.connection = (
            await connection.Connection.connect_controller(
                controller_name, max_frame_size=self.max_frame_size))
        self.controller_name = controller_name

    async def disconnect(self):
        """Shut down the watcher task and close websockets.

        """
        if self.connection and self.connection.is_open:
            log.debug('Closing controller connection')
            await self.connection.close()
            self.connection = None

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
            owner = self.connection.info['user-info']['identity']

        if credential and not name:
            raise errors.JujuError('Name must be provided for credential')

        if not credential:
            name, credential = connection.JujuData().load_credential(cloud,
                                                                     name)
            if credential is None:
                raise errors.JujuError('Unable to find credential: '
                                       '{}'.format(name))

        log.debug('Uploading credential %s', name)
        cloud_facade = client.CloudFacade.from_connection(self.connection)
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

        """
        model_facade = client.ModelManagerFacade.from_connection(
            self.connection)

        owner = owner or self.connection.info['user-info']['identity']
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
                loop=self.loop)

        model_info = await model_facade.CreateModel(
            tag.cloud(cloud_name),
            config,
            credential,
            model_name,
            owner,
            region
        )

        model = Model()
        await model.connect(
            self.connection.endpoint,
            model_info.uuid,
            self.connection.username,
            self.connection.password,
            self.connection.cacert,
            self.connection.macaroons,
            loop=self.loop,
        )

        return model

    async def destroy_models(self, *models):
        """Destroy one or more models.

        :param str \*models: Names or UUIDs of models to destroy

        """
        uuids = await self.model_uuids()
        models = [uuids[model] if model in uuids else model
                  for model in models]

        model_facade = client.ModelManagerFacade.from_connection(
            self.connection)

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
        user_facade = client.UserManagerFacade.from_connection(self.connection)
        users = [client.AddUser(display_name=display_name,
                                username=username,
                                password=password)]
        await user_facade.AddUser(users)
        return await self.get_user(username)

    async def remove_user(self, username):
        """Remove a user from this controller.
        """
        client_facade = client.UserManagerFacade.from_connection(
            self.connection)
        user = tag.user(username)
        await client_facade.RemoveUser([client.Entity(user)])

    async def change_user_password(self, username, password):
        """Change the password for a user in this controller.

        :param str username: Username
        :param str password: New password

        """
        user_facade = client.UserManagerFacade.from_connection(self.connection)
        entity = client.EntityPassword(password, tag.user(username))
        return await user_facade.SetPassword([entity])

    async def destroy(self, destroy_all_models=False):
        """Destroy this controller.

        :param bool destroy_all_models: Destroy all hosted models in the
            controller.

        """
        controller_facade = client.ControllerFacade.from_connection(
            self.connection)
        return await controller_facade.DestroyController(destroy_all_models)

    async def disable_user(self, username):
        """Disable a user.

        :param str username: Username

        """
        user_facade = client.UserManagerFacade.from_connection(self.connection)
        entity = client.Entity(tag.user(username))
        return await user_facade.DisableUser([entity])

    async def enable_user(self, username):
        """Re-enable a previously disabled user.

        """
        user_facade = client.UserManagerFacade.from_connection(self.connection)
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
        cloud_facade = client.CloudFacade.from_connection(self.connection)

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
            self.connection)
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
                await asyncio.sleep(attempt, loop=self.loop)

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

        """
        uuids = await self.model_uuids()
        if model in uuids:
            name_or_uuid = uuids[model]
        else:
            name_or_uuid = model

        model = Model()
        await model.connect(
            self.connection.endpoint,
            name_or_uuid,
            self.connection.username,
            self.connection.password,
            self.connection.cacert,
            self.connection.macaroons,
            loop=self.loop,
        )
        return model

    async def get_user(self, username):
        """Get a user by name.

        :param str username: Username
        :returns: A :class:`~juju.user.User` instance
        """
        client_facade = client.UserManagerFacade.from_connection(
            self.connection)
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
            self.connection)
        response = await client_facade.UserInfo(None, include_disabled)
        return [User(self, r.result) for r in response.results]

    async def grant(self, username, acl='login'):
        """Set access level of the given user on the controller

        :param str username: Username
        :param str acl: Access control ('login', 'add-model' or 'superuser')

        """
        controller_facade = client.ControllerFacade.from_connection(
            self.connection)
        user = tag.user(username)
        await self.revoke(username)
        changes = client.ModifyControllerAccess(acl, 'grant', user)
        return await controller_facade.ModifyControllerAccess([changes])

    async def revoke(self, username):
        """Removes all access from a controller

        :param str username: username

        """
        controller_facade = client.ControllerFacade.from_connection(
            self.connection)
        user = tag.user(username)
        changes = client.ModifyControllerAccess('login', 'revoke', user)
        return await controller_facade.ModifyControllerAccess([changes])
