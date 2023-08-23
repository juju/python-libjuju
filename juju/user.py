# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import logging

import pyrfc3339

from . import tag, errors
from .client import client

log = logging.getLogger(__name__)


class User(object):
    def __init__(self, controller, user_info, secret_key=None):
        self.controller = controller
        self._user_info = user_info
        self._secret_key = secret_key

    @property
    def tag(self):
        return tag.user(self.username)

    @property
    def username(self):
        return self._user_info.username

    @property
    def display_name(self):
        return self._user_info.display_name

    @property
    def last_connection(self):
        return pyrfc3339.parse(self._user_info.last_connection)

    @property
    def access(self):
        """Identifies the controller access levels of this user"""
        return self._user_info.access

    @property
    def date_created(self):
        return self._user_info.date_created

    @property
    def enabled(self):
        return not self._user_info.disabled

    @property
    def disabled(self):
        return self._user_info.disabled

    @property
    def created_by(self):
        return self._user_info.created_by

    @property
    def secret_key(self):
        return self._secret_key

    async def set_password(self, password):
        """Update this user's password.
        """
        await self.controller.change_user_password(self.username, password)
        self._user_info.password = password

    async def modify_model_access(self, acl, action, model_name):
        """Grants or revokes the given access level for this user for a given model

        :param str acl: Model access levels (see access module)
        :param str action: grant/revoke
        :param str model_name: Name of the model

        :return bool: True if access changed, Error if user already has it
        """
        modelmanager_facade = client.ModelManagerFacade.from_connection(
            self.controller.connection())
        models = await self.controller.model_uuids()
        if model_name not in models:
            raise errors.JujuError(f'Unable to find model : {model_name}')
        changes = client.ModifyModelAccess(acl, action, tag.model(models[model_name]), self.tag)
        await modelmanager_facade.ModifyModelAccess(changes=[changes])
        return True

    async def modify_controller_access(self, acl, action):
        """Grants or revokes the given access level for this user on the current controller

        :param str acl: Controller access levels (see access module)
        :param str action: grant/revoke

        :return bool: True if access changed, Error if user already has it
        """
        controller_facade = client.ControllerFacade.from_connection(self.controller.connection())
        changes = client.ModifyControllerAccess(acl, action, self.tag)
        await controller_facade.ModifyControllerAccess(changes=[changes])

        new_access = acl
        if action == 'revoke':
            new_access = ''
        self._user_info.access = new_access
        return True

    async def modify_offer_access(self, acl, action, offer_url):
        """Grants or revokes the given access level for this user on a given offer

        :param str acl: Controller access levels (see access module)
        :param str action: grant/revoke
        :param str offer_url: url for the offer

        :return bool: True if access changed, Error if user already has it
        """
        application_offers_facade = client.ApplicationOffersFacade.from_connection(
            self.controller.connection())
        changes = client.ModifyOfferAccess(acl, action, offer_url, self.tag)
        await application_offers_facade.ModifyOfferAccess(changes=[changes])
        return True

    async def grant_or_revoke(self, acl, action, **kwargs):
        """Grants or revokes the given access level of this user on model, offer or controller,
        depending on the access level (see the access module)

        :param str acl: Access control level
        :param str action: 'grant' or 'revoke'

        Depending on the access level, the available keyword parameters are:
        :param str model_name: name of the model if acl is one of model access levels
        :param str offer_url: url for the offer if acl is one of offer access levels

        :return: True if access changed, False if user already has it
        """
        try:
            if 'model_name' in kwargs:
                return await self.modify_model_access(acl, action, kwargs['model_name'])
            elif 'offer_url' in kwargs:
                return await self.modify_offer_access(acl, action, kwargs['offer_url'])
            else:
                return await self.modify_controller_access(acl, action)
        except errors.JujuError as e:
            if 'user already has' in str(e):
                return False
            else:
                raise

    async def grant(self, acl, **kwargs):
        """Grant the given access level of this user on model, offer or controller, depending on
        the access level (see the access module)

        :param str acl: Access control level

        Depending on the access level, the available keyword parameters are:
        :param str model_name: name of the model if acl is one of model access levels
        :param str offer_url: url for the offer if acl is one of offer access levels

        :return: None or Error
        """
        return await self.grant_or_revoke(acl, 'grant', **kwargs)

    async def revoke(self, acl='login', **kwargs):
        """The opposite of user.grant(). Revokes the given access level of this user on model,
        offer or controller, depending on the given access level.

        :param str acl: Access control level (see access module)

        Available keyword parameters are:
        :param str model_name: name of the model if acl is one of model access levels
        :param str offer_url: url for the offer if acl is one of offer access levels
        """
        return await self.grant_or_revoke(acl, 'revoke', **kwargs)

    async def disable(self):
        """Disable this user.
        """
        await self.controller.disable_user(self.username)
        self._user_info.disabled = True

    async def enable(self):
        """Re-enable this user.
        """
        await self.controller.enable_user(self.username)
        self._user_info.disabled = False
