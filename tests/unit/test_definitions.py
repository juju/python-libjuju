import unittest

from juju.client import client


class TestDefinitions(unittest.TestCase):

    def test_dict_legacy(self):
        status = client.FullStatus.from_json({
            'relations': [{
                'endpoints': [{
                    'application': 'application',
                    'name': 'name',
                    'role': 'role',
                    'subordinate': True
                }],
                'id': 1,
                'interface': 'interface',
                'key': 'key',
                'scope': 'scope',
                'status': []
            }]
        })
        if status.relations != status['relations']:
            raise Exception('subscript not equal to attr')
        if status.relations != status.get('relations'):
            raise Exception('get() not equal to attr')
        if status.get('non-existing', 'foo') != 'foo':
            raise Exception('get defaulting missing attr')

    def test_parse(self):
        status = client.FullStatus.from_json({
            'relations': [{
                'endpoints': [{
                    'application': 'application',
                    'name': 'name',
                    'role': 'role',
                    'subordinate': True
                }],
                'id': 1,
                'interface': 'interface',
                'key': 'key',
                'scope': 'scope',
                'status': []
            }],
            'applications': {
                'app': {
                    'can-upgrade-to': 'something',
                    'charm': 'charm',
                    'charm-profile': 'profile',
                    'charm-version': '2',
                    'endpoint-bindings': None,
                    'err': None,
                    'exposed': True,
                    'int': 0,
                    'life': 'life',
                    'meter-statuses': {},
                    'provider-id': 'provider-id',
                    'public-address': '1.1.1.1',
                    'relations': {
                        'a': ['b', 'c'],
                    },
                    'series': 'focal',
                    'status': {},
                    'subordinate-to': ['other'],
                    'units': {
                        'unit-id': {
                            'address': '1.1.1.1',
                            'agent-status': {},
                            'charm': 'charm',
                            'leader': True,
                            'machine': 'machine-0',
                            'opened-ports': ['1234'],
                            'provider-id': 'provider',
                            'public-address': '1.1.1.2',
                            'subordinates': {},
                            'workload-status': {},
                            'workload-version': '1.2'
                        }
                    },
                    'workload-version': '1.2'
                }
            }
        })
        if status.relations != status['relations']:
            raise Exception('subscript not equal to attr')
        if status['relations'][0]['endpoints'][0]['application'] != 'application':
            raise Exception('failed to use complex subscript')
        if status.applications['app'].relations['a'][0] != 'b':
            raise Exception('object with array type is invalid')
        if not isinstance(status.relations[0], client.RelationStatus):
            raise Exception('status relation is not a RelationStatus')
        if not isinstance(status.relations[0].endpoints[0], client.EndpointStatus):
            raise Exception('status relation endpoint is not a EndpointStatus')
        if not isinstance(status.applications['app'], client.ApplicationStatus):
            raise Exception('status application is not a ApplicationStatus')
