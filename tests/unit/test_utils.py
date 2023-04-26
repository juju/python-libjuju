import unittest
import pytest

from juju.utils import series_selector, get_base_from_origin_or_channel, parse_base_arg, juju_config_dir, juju_ssh_key_paths, DEFAULT_SUPPORTED_LTS
from juju.client import client
from juju.errors import JujuError
from juju.url import URL


class TestDirResolve(unittest.TestCase):
    def test_config_dir(self):
        config_dir = juju_config_dir()
        assert 'local/share/juju' in config_dir

    def test_juju_ssh_key_paths(self):
        public, private = juju_ssh_key_paths()
        assert public.endswith('ssh/juju_id_rsa.pub')
        assert private.endswith('ssh/juju_id_rsa')


class TestBaseArgument(unittest.TestCase):
    def test_parse_base_arg(self):
        base = parse_base_arg('ubuntu@22.04')
        assert isinstance(base, client.Base)
        assert base.name == 'ubuntu'
        assert base.channel == '22.04'


class TestBaseFromSeries(unittest.TestCase):
    def test_get_base_from_series(self):
        b = get_base_from_origin_or_channel(client.CharmOrigin(track='latest', risk='edge'), series='jammy')
        assert b.name == 'ubuntu'
        assert b.channel == '22.04/edge'


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
