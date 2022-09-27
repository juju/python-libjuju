from .client import client
from .errors import JujuError
from juju import jasyncio

import requests
import json


class CharmHub:
    def __init__(self, model):
        self.model = model

    def request_charmhub_with_retry(self, url, retries):
        for attempt in range(retries):
            _response = requests.get(url)
            if _response.status_code == 200:
                return _response
            jasyncio.sleep(5)
        raise JujuError("Got {} from {}".format(_response.status_code, url))

    async def get_charm_id(self, charm_name):
        conn, headers, path_prefix = self.model.connection().https_connection()

        model_conf = await self.model.get_config()
        charmhub_url = model_conf['charmhub-url']
        url = "{}/v2/charms/info/{}".format(charmhub_url.value, charm_name)
        _response = self.request_charmhub_with_retry(url, 5)
        response = json.loads(_response.text)
        return response['id'], response['name']

    async def is_subordinate(self, charm_name):
        conn, headers, path_prefix = self.model.connection().https_connection()

        model_conf = await self.model.get_config()
        charmhub_url = model_conf['charmhub-url']
        url = "{}/v2/charms/info/{}?fields=default-release.revision.subordinate".format(charmhub_url.value, charm_name)
        _response = self.request_charmhub_with_retry(url, 5)
        response = json.loads(_response.text)
        return 'subordinate' in response['default-release']['revision']

    # TODO (caner) : we should be able to recreate the channel-map through the
    #  api call without needing the CharmHub facade

    async def list_resources(self, charm_name):
        conn, headers, path_prefix = self.model.connection().https_connection()

        model_conf = await self.model.get_config()
        charmhub_url = model_conf['charmhub-url']
        url = "{}/v2/charms/info/{}?fields=default-release.resources".format(charmhub_url.value, charm_name)
        _response = self.request_charmhub_with_retry(url, 5)
        response = json.loads(_response.text)
        return response['default-release']['resources']

    async def info(self, name, channel=None):
        """info displays detailed information about a CharmHub charm. The charm
        can be specified by the exact name.

        Channel is a hint for providing the metadata for a given channel.
        Without the channel hint then only the default release will have the
        metadata.

        """
        if not name:
            raise JujuError("name expected")

        if channel is None:
            channel = ""

        facade = self._facade()
        return await facade.Info(tag="application-{}".format(name), channel=channel)

    async def find(self, query, category=None, channel=None,
                   charm_type=None, platforms=None, publisher=None,
                   relation_requires=None, relation_provides=None):
        """find queries the CharmHub store for available charms or bundles.

        """
        if charm_type is not None and charm_type not in ["charm", "bundle"]:
            raise JujuError("expected either charm or bundle for charm_type")

        facade = self._facade()
        return await facade.Find(query=query, category=category, channel=channel,
                                 type_=charm_type, platforms=platforms, publisher=publisher,
                                 relation_provides=relation_provides, relation_requires=relation_requires)

    def _facade(self):
        return client.CharmHubFacade.from_connection(self.model.connection())
