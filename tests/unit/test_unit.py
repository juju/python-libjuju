import asynctest
import mock
import pytest

from juju.model import Model
from juju.unit import Unit
from juju.client._definitions import FullStatus

from .. import base


@asynctest.patch('juju.client.client.ClientFacade')
@pytest.mark.asyncio
async def test_unit_is_leader(mock_cf):
    tests = [
        {
            'applications': {
                'test': {
                    'units': {
                        'test/0': {
                            'subordinates': {
                                'test-sub/0': {
                                    'leader': True
                                }
                            }
                        }
                    }
                },
                'test-sub': {
                    'subordinate-to': [
                        'test'
                    ]
                }
            },
            'description': "Tests that subordinate units reports is leader correctly",
            'unit': 'test-sub/0',
            'rval': True
        },
        {
            'applications': {
                'test': {
                    'units': {
                        'test/0': {
                            'leader': True
                        }
                    }
                }
            },
            'description': "Tests that unit reports is leader correctly",
            'unit': 'test/0',
            'rval': True
        },
        {
            'applications': {},
            'description': "Tests that non existent apps return False as leader",
            'unit': 'test/0',
            'rval': False
        },
        {
            'applications': {
                'test': {
                    'units': {}
                }
            },
            'description': "Tests that apps with no units report False as leader",
            'unit': 'test/0',
            'rval': False
        },
        {
            'applications': {
                'test': {
                    'units': {
                        'test/0': {
                            'subordinates': {
                                'test-sub/0': {}
                            }
                        }
                    }
                },
                'test1': {
                    'units': {
                        'test1/0': {
                            'subordinates': {
                                'test-sub/1': {
                                    'leader': True
                                }
                            }
                        }
                    }
                },
                'test-sub': {
                    'subordinate-to': [
                        'test',
                        'test1'
                    ]
                }
            },
            'description': "Tests that subordinate units of multiple applications reports is leader correctly",
            'unit': 'test-sub/1',
            'rval': True
        },
        {
            'applications': {
                'test': {
                    'units': {
                        'test/0': {
                            'subordinates': {
                                'test-sub/0': {
                                    'leader': True
                                }
                            }
                        }
                    }
                },
                'test1': {
                    'units': {
                        'test1/0': {
                            'subordinates': {
                                'test-sub/1': {}
                            }
                        }
                    }
                },
                'test-sub': {
                    'subordinate-to': [
                        'test',
                        'test1'
                    ]
                }
            },
            'description': "Tests that subordinate units of multiple applications reports is leader correctly",
            'unit': 'test-sub/1',
            'rval': False
        }
    ]

    model = Model()
    model._connector = mock.MagicMock()

    for test in tests:
        status = FullStatus.from_json(test)
        client_facade = mock_cf.from_connection()
        client_facade.FullStatus = base.AsyncMock(return_value=status)

        unit = Unit("test", model)
        unit.name = test['unit']

        rval = await unit.is_leader_from_status()
        assert rval == test['rval']
