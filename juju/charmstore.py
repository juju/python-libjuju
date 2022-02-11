from functools import partial

import theblues.charmstore
import theblues.errors

from urllib.parse import urlencode


from . import jasyncio


class CharmStore:
    """
    Async wrapper around theblues.charmstore.CharmStore
    """
    DEFAULT_INCLUDES = theblues.charmstore.DEFAULT_INCLUDES
    _get_path = theblues.charmstore._get_path

    def __init__(self, cs_timeout=20):
        self._cs = theblues.charmstore.CharmStore(timeout=cs_timeout)

    def _resources(self, entity_id, channel=None):
        '''
        Retrieve metadata about the resources of an entity in the charmstore.
        This data was previously available in the charmstore API but is no longer included
        with charmhub compatibility.  However, another API to retrieve the same
        information is available.

        @param entity_id The ID either a reference or a string of the entity
               to get.
        '''
        url = '{}/{}/meta/resources'.format(self._cs.url,
                                            CharmStore._get_path(entity_id))
        if isinstance(channel, str):
            url += '?{}'.format(urlencode({"channel": channel}))

        try:
            data = self._cs._get(url)
        except theblues.charmstore.EntityNotFound:
            return {}
        return data.json()

    def _entity(self, *args, **kwargs):
        '''
        Overloads the method from theblues.charmstore.CharmStore
        by fetching entity information and additional resources listings
        in the event other application level code expected to continue
        fetching this information.

        Get the default data for any entity (e.g. bundle or charm).

        @param entity_id The entity's id either as a reference or a string
        @param get_files Whether to fetch the files for the charm or not.
        @param channel Optional channel name.
        @param include_stats Optionally disable stats collection.
        @param includes An optional list of meta info to include, as a
               sequence of strings. If None, the default include list is used.
        '''
        includes = kwargs.get('includes')
        if not includes:
            includes = kwargs["includes"] = CharmStore.DEFAULT_INCLUDES + ["id"]

        result = self._cs.entity(*args, **kwargs)
        if "resources" in includes:
            resources = self._resources(result["Id"], channel=kwargs.get("channel"))
            result['Meta']['resources'] = resources
        return result

    def __getattr__(self, name):
        """
        Wrap method calls in coroutines that use run_in_executor to make them
        async.
        """
        if name == "entity":
            attr = self._entity
        else:
            attr = getattr(self._cs, name)
        if not callable(attr):
            wrapper = partial(getattr, self._cs, name)
            setattr(self, name, wrapper)
        else:
            async def coro(*args, **kwargs):
                method = partial(attr, *args, **kwargs)
                for attempt in range(1, 4):
                    try:
                        loop = jasyncio.get_running_loop()
                        return await loop.run_in_executor(None, method)
                    except theblues.errors.ServerError:
                        if attempt == 3:
                            raise
                        await jasyncio.sleep(1)
            setattr(self, name, coro)
            wrapper = coro
        return wrapper
