"""
Tests for generated client code

"""

import mock

from juju.client import client


def test_basics():
    assert client.CLIENTS
    for i in range(1, 5):  # Assert versions 1-4 in client dict
        assert str(i) in client.CLIENTS


def test_from_connection():
    connection = mock.Mock()
    connection.facades = {"Action": 2}
    action_facade = client.ActionFacade.from_connection(connection)
    assert action_facade


def test_to_json():
    uml = client.UserModelList([client.UserModel()])
    assert uml.to_json() == ('{"user-models": [{"last-connection": null, '
                             '"model": null}]}')
