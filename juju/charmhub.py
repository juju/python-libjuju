# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from .client import client
from .errors import JujuError
from juju import jasyncio

import requests
import json


class CharmHub:
    def __init__(self, model):
        self.model = model

    async def _charmhub_url(self):
        model_conf = await self.model.get_config()
        return model_conf['charmhub-url']

    async def request_charmhub_with_retry(self, url, retries):
        for attempt in range(retries):
            _response = requests.get(url)
            if _response.status_code == 200:
                return _response
            await jasyncio.sleep(5)
        raise JujuError("Got {} from {}".format(_response.status_code, url))

    async def get_charm_id(self, charm_name):
        conn, headers, path_prefix = self.model.connection().https_connection()

        charmhub_url = await self._charmhub_url()
        url = "{}/v2/charms/info/{}".format(charmhub_url.value, charm_name)
        _response = await self.request_charmhub_with_retry(url, 5)
        response = json.loads(_response.text)
        return response['id'], response['name']

    async def is_subordinate(self, charm_name):
        conn, headers, path_prefix = self.model.connection().https_connection()

        charmhub_url = await self._charmhub_url()
        url = "{}/v2/charms/info/{}?fields=default-release.revision.subordinate".format(charmhub_url.value, charm_name)
        _response = await self.request_charmhub_with_retry(url, 5)
        response = json.loads(_response.text)
        rev_response = response['default-release']['revision']
        return 'subordinate' in rev_response and rev_response['subordinate']

    # TODO (caner) : we should be able to recreate the channel-map through the
    #  api call without needing the CharmHub facade

    async def list_resources(self, charm_name):
        conn, headers, path_prefix = self.model.connection().https_connection()

        charmhub_url = await self._charmhub_url()
        url = "{}/v2/charms/info/{}?fields=default-release.resources".format(charmhub_url.value, charm_name)
        _response = await self.request_charmhub_with_retry(url, 5)
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

        if self.model.connection().is_using_old_client:
            if channel is None:
                channel = ""
            facade = self._facade()
            res = await facade.Info(tag="application-{}".format(name),
                                    channel=channel)
            err_code = res.errors.error_list.code
            if err_code:
                raise JujuError(f'charmhub.info - {err_code} :'
                                f' {res.errors.error_list.message}')
            result = res.result
            result.channel_map = CharmHub._channel_map_to_dict(
                result.channel_map,
                name,
                channel=channel)
            result = result.serialize()
        else:
            charmhub_url = await self._charmhub_url()
            url = "{}/v2/charms/info/{}?fields=channel-map".format(
                charmhub_url.value, name)
            try:
                _response = await self.request_charmhub_with_retry(url, 5)
            except JujuError as e:
                if '404' in e.message:
                    raise JujuError(f'{name} not found') from e
            result = json.loads(_response.text)
            result['channel-map'] = CharmHub._channel_list_to_map(result['channel-map'],
                                                                  name,
                                                                  channel=channel)
        return result

    @staticmethod
    def _channel_list_to_map(channel_list_map, name, channel=""):
        """Charmhub API returns the channel map as a list of channel objects
        (with risk, track, revision, download etc). This turns that into a map
        that's keyed with the channel=track/risk for easy
        filtering/processing. This representation is also closer to the
        result of the 2.9 facade call.

        So basically,
        [{'channel':{'risk':'stable', 'track':'latest'}, 'revision': 58}]
          becomes:
        {'latest/stable': {'channel':{'risk':'stable', 'track':'latest'},
        'revision': 58}}

        :param channel_list_map: [map[str][any]]
        :return: map[str][map[str][any]]
        """
        channel_map = {}
        for ch in channel_list_map:
            ch_name = f"{ch['channel']['track']}/{ch['channel']['risk']}"
            if channel and channel != ch_name:
                # If channel is given, then filter out the rest
                continue
            channel_map[ch_name] = ch
            if channel == ch_name:
                # If we found the desired channel, no need to continue
                break
        # After loop is done, check for non-existent channel
        if channel and channel not in channel_map:
            raise JujuError(f'Charmhub.info : channel {channel} not found for'
                            f' {name}')
        return channel_map

    @staticmethod
    def _channel_map_to_dict(channel_map, name, channel=""):
        """Converts the client.definitions.Channel objects into python maps
        inside a channel map (for pylibjuju <3.0)

        :param channel_map: map[str][Channel]
        :return: map[str][map[str][any]]
        """
        channel_dict = {}
        for ch_name, ch_obj in channel_map.items():
            # No need to worry about filtering channel
            # Charmhub facade will take care of that
            _ch = ch_obj.serialize()
            _ch['platforms'] = [p.serialize() for p in _ch['platforms']]
            channel_dict[ch_name] = _ch
        if channel and channel not in channel_dict:
            raise JujuError(f'Charmhub.info : channel {channel} not found for'
                            f' {name}')
        return channel_dict

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
