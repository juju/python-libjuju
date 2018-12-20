import logging

import pyrfc3339

from . import tag

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

    async def grant(self, acl='login'):
        """Set access level of this user on the controller.

        :param str acl: Access control ('login', 'add-model', or 'superuser')
        """
        if await self.controller.grant(self.username, acl):
            self._user_info.access = acl

    async def revoke(self):
        """Removes all access rights for this user from the controller.
        """
        await self.controller.revoke(self.username)
        self._user_info.access = ''

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
