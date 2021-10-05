import unittest

from juju.utils import juju_config_dir, juju_ssh_key_paths


class TestDirResolve(unittest.TestCase):
    def test_config_dir(self):
        config_dir = juju_config_dir()
        assert 'local/share/juju' in config_dir

    def test_juju_ssh_key_paths(self):
        public, private = juju_ssh_key_paths()
        assert public.endswith('ssh/juju_id_rsa.pub')
        assert private.endswith('ssh/juju_id_rsa')
