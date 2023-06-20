import unittest

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
