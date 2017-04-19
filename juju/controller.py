import asyncio
import logging

from . import tag
from . import utils
from .client import client
from .client import connection
from .model import Model

log = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, loop=None):
        """Instantiate a new Controller.

        One of the connect_* methods will need to be called before this
        object can be used for anything interesting.

        :param loop: an asyncio event loop

        """
        self.loop = loop or asyncio.get_event_loop()
        self.connection = None
        self.controller_name = None

    async def connect(
            self, endpoint, username, password, cacert=None, macaroons=None):
        """Connect to an arbitrary Juju controller.

        """
        self.connection = await connection.Connection.connect(
            endpoint, None, username, password, cacert, macaroons)

    async def connect_current(self):
        """Connect to the current Juju controller.

        """
        self.connection = (
            await connection.Connection.connect_current_controller())

    async def connect_controller(self, controller_name):
        """Connect to a Juju controller by name.

        """
        self.connection = (
            await connection.Connection.connect_controller(controller_name))
        self.controller_name = controller_name

    async def disconnect(self):
        """Shut down the watcher task and close websockets.

        """
        if self.connection and self.connection.is_open:
            log.debug('Closing controller connection')
            await self.connection.close()
            self.connection = None

    async def add_model(
            self, model_name, cloud_name=None, credential_name=None,
            owner=None, config=None, region=None):
        """Add a model to this controller.

        :param str model_name: Name to give the new model.
        :param str cloud_name: Name of the cloud in which to create the
            model, e.g. 'aws'. Defaults to same cloud as controller.
        :param str credential_name: Name of the credential to use when
            creating the model. Defaults to current credential. If you
            pass a credential_name, you must also pass a cloud_name,
            even if it's the default cloud.
        :param str owner: Username that will own the model. Defaults to
            the current user.
        :param dict config: Model configuration.
        :param str region: Region in which to create the model.

        """
        model_facade = client.ModelManagerFacade.from_connection(
            self.connection)

        owner = owner or self.connection.info['user-info']['identity']
        cloud_name = cloud_name or await self.get_cloud()

        if credential_name:
            credential = tag.credential(
                cloud_name,
                tag.untag('user-', owner),
                credential_name
            )
        else:
            credential = None

        log.debug('Creating model %s', model_name)

        model_info = await model_facade.CreateModel(
            tag.cloud(cloud_name),
            config,
            credential,
            model_name,
            owner,
            region
        )

        # Add our ssh key to the model, to work around
        # https://bugs.launchpad.net/juju/+bug/1643076
        try:
            ssh_key = await utils.read_ssh_key(loop=self.loop)

            if self.controller_name:
                model_name = "{}:{}".format(self.controller_name, model_name)

            cmd = ['juju', 'add-ssh-key', '-m', model_name, ssh_key]

            await utils.execute_process(*cmd, log=log, loop=self.loop)
        except Exception:
            log.exception(
                "Could not add ssh key to model. You will not be able "
                "to ssh into machines in this model. "
                "Manually running `juju add-ssh-key <key>` in the cli "
                "may fix this problem.")

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

    async def destroy_models(self, *uuids):
        """Destroy one or more models.

        :param str \*uuids: UUIDs of models to destroy

        """
        model_facade = client.ModelManagerFacade.from_connection(
            self.connection)

        log.debug(
            'Destroying model%s %s',
            '' if len(uuids) == 1 else 's',
            ', '.join(uuids)
        )

        await model_facade.DestroyModels([
            client.Entity(tag.model(uuid))
            for uuid in uuids
        ])
    destroy_model = destroy_models

    async def add_user(self, username, password=None, display_name=None):
        """Add a user to this controller.

        :param str username: Username
        :param str display_name: Display name
        :param str acl: Access control, e.g. 'read'
        :param list models: Models to which the user is granted access

        """
        if not display_name:
            display_name = username
        user_facade = client.UserManagerFacade.from_connection(self.connection)
        users = [{'display_name': display_name,
                  'password': password,
                  'username': username}]
        return await user_facade.AddUser(users)

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
        """Return list of available models on this controller.

        :param bool all_: List all models, regardless of user accessibilty
            (admin use only)
        :param str username: User for which to list models (admin use only)

        """
        controller_facade = client.ControllerFacade.from_connection(
            self.connection)
        return await controller_facade.AllModels()


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

    def get_users(self, all_=False):
        """Return list of users that can connect to this controller.

        :param bool all_: Include disabled users

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

    def get_model(self, name):
        """Get a model by name.

        :param str name: Model name

        """
        raise NotImplementedError()

    async def get_user(self, username, include_disabled=False):
        """Get a user by name.

        :param str username: Username

        """
        client_facade = client.UserManagerFacade.from_connection(
            self.connection)
        user = tag.user(username)
        return await client_facade.UserInfo([client.Entity(user)], include_disabled)

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
