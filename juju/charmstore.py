from functools import partial
from contextlib import closing
import io
import zipfile

import theblues.charmstore
import theblues.errors

from urllib.parse import urlencode

from .errors import JujuError

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

    def _files(self, entity_id, manifest=None, filename=None, read_file=False, channel=None):
        '''
        Overloads the files method from theblues.charmstore.CharmStore
        that method used APIs which are no longer implemented
        https://api.snapcraft.io/docs/charm-compat-api.html

        Get the files or file contents of a file for an entity.

        If filename is provided and read_file is true, the *contents* of the
        file are returned, if the file exists.

        @param entity_id The id of the entity to get files for
        @param filename  The name of the file in the archive to get.
        @param manifest  Remains for compatibility but is unused
        @param read_file Whether to get the url for the file or the file
            contents.
        @param channel Optional channel name.
        '''
        assert read_file, "This method no longer supports returning a dictionary of URLs to files"
        archive_resp = self._cs._get(self._cs.archive_url(entity_id, channel))
        with closing(archive_resp), zipfile.ZipFile(io.BytesIO(archive_resp.content)) as archive:
            for member in archive.infolist():
                if member.filename == filename:
                    return archive.read(member)
            raise JujuError("{} not found".format(filename))

    def __getattr__(self, name):
        """
        Wrap method calls in coroutines that use run_in_executor to make them
        async.
        """
        if name == "entity":
            attr = self._entity
        elif name == "files":
            attr = self._files
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
