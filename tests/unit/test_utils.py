# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import unittest
import pytest

from juju.utils import series_selector, get_base_from_origin_or_channel, \
    parse_base_arg, DEFAULT_SUPPORTED_LTS, get_series_version, \
    get_version_series, base_channel_to_series, \
    base_channel_from_series, get_os_from_series
from juju.errors import JujuError
from juju.url import URL
from juju import utils
from juju.client import client


class TestDirResolve(unittest.TestCase):
    def test_config_dir(self):
        config_dir = utils.juju_config_dir()
        assert 'local/share/juju' in config_dir

    def test_juju_ssh_key_paths(self):
        public, private = utils.juju_ssh_key_paths()
        assert public.endswith('ssh/juju_id_rsa.pub')
        assert private.endswith('ssh/juju_id_rsa')


class TestBaseArgument(unittest.TestCase):
    def test_parse_base_arg(self):
        base = parse_base_arg('ubuntu@22.04')
        assert isinstance(base, client.Base)
        assert base.name == 'ubuntu'
        assert base.channel == '22.04'


class TestSeriesSelector(unittest.TestCase):
    def test_series_arg(self):
        assert series_selector('jammy', []) == 'jammy'
        assert series_selector('jammy', ['jammy']) == 'jammy'
        with pytest.raises(JujuError):
            series_selector(series_arg='jammy', supported_series=['focal'])
        assert series_selector(series_arg='foo', supported_series=[], force=True) == 'foo'

    def test_charm_url(self):
        assert series_selector(charm_url=URL.parse('ch:jammy/ubuntu'), supported_series=['jammy']) == 'jammy'

    def test_model_config(self):
        mconf = {'default-base': client.ConfigValue(value='ubuntu@22.04')}
        assert series_selector(model_config=mconf, supported_series=['jammy']) == 'jammy'

    def test_charm_list_series(self):
        assert series_selector(supported_series=['focal', 'jammy']) == 'jammy'

    def test_return_lts(self):
        assert series_selector() == DEFAULT_SUPPORTED_LTS


class TestBaseChannelOriginUtils(unittest.TestCase):
    def test_get_series_version(self):
        assert get_series_version(series_name='kubernetes') == 'kubernetes'
        assert get_series_version(series_name='jammy') == '22.04'

    def test_get_version_series(self):
        assert get_version_series(version='22.04') == 'jammy'

    def test_base_channel_to_series(self):
        assert base_channel_to_series(channel='22.04/stable') == 'jammy'

    def test_base_channel_from_series(self):
        assert base_channel_from_series(track='latest', risk='stable', series='jammy') == \
               '22.04/stable'

    def test_get_os_from_series(self):
        assert get_os_from_series('jammy') == 'ubuntu'

    def test_get_base_from_series(self):
        orgn = client.CharmOrigin(track='latest', risk='edge')
        assert get_base_from_origin_or_channel(orgn, series='jammy') == client.Base('22.04/edge', 'ubuntu')


class TestShouldUpgradeResource(unittest.TestCase):
    def test_should_upgrade_resource_no_same_rev(self):
        # fields are trimmed for readability
        res = {'created-at': '2019-10-24T20:45:19.201000',
               'description': 'The policy.d overrides file',
               'download': {'hash-sha-256': 'e3b0c4', 'hash-sha-384': '38b060a751ac914898b95b',
                            'hash-sha-512': 'cf83e1357eef1a538327af927da3e',
                            'hash-sha3-384': '0c63a75b1bbed1e058d5f004',
                            'size': 0,
                            'url': 'https://api.charmhub.io/api/v1/resMGU0L516cGTTwNam.policyd-override_0'},
               'filename': 'policyd-override.zip', 'name': 'policyd-override', 'revision': 0, 'type': 'file'}

        existing = {
            'policyd-override':
                client.Resource(charmresource=None,
                                application='keystone', id_='keystone/policyd-override', pending_id='',
                                timestamp='0001-01-01T00:00:00Z', username='', name='policyd-override',
                                origin='store', type='file', path='policyd-override.zip',
                                description='The policy.doverrides file',
                                revision=0, fingerprint='OLBgp1GsljhM2TJ+sbHjaiH9txEUvgdDTAzHv2P24donTt6/529l+9Ua0vFImLlb',
                                size=0)}
        assert not utils.should_upgrade_resource(res, existing)

    def test_should_upgrade_resource_no_local_upload(self):
        # fields are trimmed for readability
        res = {'created-at': '2019-10-24T20:45:19.201000',
               'description': 'The policy.d overrides file',
               'download': {'hash-sha-256': 'e3b0c4', 'hash-sha-384': '38b060a751ac914898b95b',
                            'hash-sha-512': 'cf83e1357eef1a538327af927da3e',
                            'hash-sha3-384': '0c63a75b1bbed1e058d5f004',
                            'size': 0,
                            'url': 'https://api.charmhub.io/api/v1/resMGU0L516cGTTwNam.policyd-override_0'},
               'filename': 'policyd-override.zip', 'name': 'local_res', 'revision': 0,
               'type': 'file'}

        existing = {
            'local_res':
                client.Resource(charmresource=None,
                                application='keystone', id_='keystone/policyd-override', pending_id='',
                                timestamp='0001-01-01T00:00:00Z', username='', name='policyd-override',
                                origin='upload', type='file', path='policyd-override.zip',
                                description='The policy.doverrides file',
                                revision=0, fingerprint='OLBgp1GsljhM2TJ+sbHjaiH9txEUvgdDTAzHv2P24donTt6/529l+9Ua0vFImLlb',
                                size=0)}
        assert not utils.should_upgrade_resource(res, existing)

    def test_should_upgrade_resource_yes_new_revision(self):
        # fields are trimmed for readability
        res = {'created-at': '2019-10-24T20:45:19.201000',
               'description': 'The policy.d overrides file',
               'download': {'hash-sha-256': 'e3b0c4', 'hash-sha-384': '38b060a751ac914898b95b',
                            'hash-sha-512': 'cf83e1357eef1a538327af927da3e',
                            'hash-sha3-384': '0c63a75b1bbed1e058d5f004',
                            'size': 0,
                            'url': 'https://api.charmhub.io/api/v1/resMGU0L516cGTTwNam.policyd-override_0'},
               'filename': 'policyd-override.zip', 'name': 'policyd-override', 'revision': 1,
               'type': 'file'}

        existing = {
            'policyd-override':
                client.Resource(charmresource=None,
                                application='keystone', id_='keystone/policyd-override', pending_id='',
                                timestamp='0001-01-01T00:00:00Z', username='', name='policyd-override',
                                origin='store', type='file', path='policyd-override.zip',
                                description='The policy.doverrides file',
                                revision=0, fingerprint='OLBgp1GsljhM2TJ+sbHjaiH9txEUvgdDTAzHv2P24donTt6/529l+9Ua0vFImLlb',
                                size=0)}
        assert utils.should_upgrade_resource(res, existing)
