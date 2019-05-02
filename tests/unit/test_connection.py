import asyncio
import json
from collections import deque

import mock
from juju.errors import JujuRedirectException
from juju.client.connection import Connection
from websockets.exceptions import ConnectionClosed

import pytest

from .. import base


class WebsocketMock:
    def __init__(self, responses):
        super().__init__()
        self.responses = deque(responses)
        self.open = True

    async def send(self, message):
        pass

    async def recv(self):
        if not self.responses:
            await asyncio.sleep(1)  # delay to give test time to finish
            raise ConnectionClosed(0, 'ran out of responses')
        return json.dumps(self.responses.popleft())

    async def close(self):
        self.open = False


@pytest.mark.asyncio
async def test_out_of_order(event_loop):
    ws = WebsocketMock([
        {'request-id': 1},
        {'request-id': 3},
        {'request-id': 2},
    ])
    expected_responses = [
        {'request-id': 1},
        {'request-id': 2},
        {'request-id': 3},
    ]
    minimal_facades = [{'name': 'Pinger', 'versions': [1]}]
    con = None
    try:
        with \
                mock.patch('websockets.connect', base.AsyncMock(return_value=ws)), \
                mock.patch(
                    'juju.client.connection.Connection.login',
                    base.AsyncMock(return_value={'response': {
                        'facades': minimal_facades,
                    }}),
                ), \
                mock.patch('juju.client.connection.Connection._get_ssl'), \
                mock.patch('juju.client.connection.Connection._pinger', base.AsyncMock()):
            con = await Connection.connect('0.1.2.3:999')
        actual_responses = []
        for i in range(3):
            actual_responses.append(await con.rpc({'version': 1}))
        assert actual_responses == expected_responses
    finally:
        if con:
            await con.close()


@pytest.mark.asyncio
async def test_bubble_redirect_exception(event_loop):
    ca_cert = """
-----BEGIN CERTIFICATE-----
SOMECERT
-----END CERTIFICATE-----"""
    ws = WebsocketMock([
        {
            'request-id': 1,
            'error': 'redirection to alternative server required',
            'error-code': 'redirection required',
            'error-info': {
                'ca-cert': ca_cert,
                'servers': [[
                    {
                        'port': 17070,
                        'scope': 'local-cloud',
                        'type': 'ipv4',
                        'value': '42.42.42.42',
                    },
                    {
                        'port': 4242,
                        'scope': 'public',
                        'type': 'ipv4',
                        'value': '42.42.42.42',
                    },
                ]],
            },
            'response': {},
        },
    ])
    with pytest.raises(JujuRedirectException) as caught_ex:
        with mock.patch('websockets.connect', base.AsyncMock(return_value=ws)):
            await Connection.connect('0.1.2.3:999')

    redir_error = caught_ex.value
    assert redir_error.follow_redirect is False
    assert redir_error.ca_cert == ca_cert
    assert redir_error.endpoints == [
        ('42.42.42.42:17070', ca_cert),
        ('42.42.42.42:4242', ca_cert),
    ]


@pytest.mark.asyncio
async def test_follow_redirect(event_loop):
    ca_cert = """
-----BEGIN CERTIFICATE-----
SOMECERT
-----END CERTIFICATE-----"""
    wsForCont1 = WebsocketMock([
        {
            'request-id': 1,
            'error': 'redirection to alternative server required',
            'error-code': 'redirection required',
            'response': {},
        },
        {
            'request-id': 2,
            'response': {
                'ca-cert': ca_cert,
                'servers': [[
                    {
                        'port': 17070,
                        'scope': 'local-cloud',
                        'type': 'ipv4',
                        'value': '42.42.42.42',
                    },
                    {
                        'port': 4242,
                        'scope': 'public',
                        'type': 'ipv4',
                        'value': '42.42.42.42',
                    },
                ]],
            },
        },
    ])
    minimal_facades = [{'name': 'Pinger', 'versions': [1]}]
    wsForCont2 = WebsocketMock([
        {'request-id': 1},
        {'request-id': 2},
        {'request-id': 3, 'response': {'result': minimal_facades}},
    ])

    con = None
    try:
        with \
            mock.patch('websockets.connect',
                       base.AsyncMock(side_effect=[wsForCont1, wsForCont2])
                       ), \
            mock.patch('juju.client.connection.Connection._get_ssl'), \
            mock.patch('juju.client.connection.Connection._pinger',
                       base.AsyncMock()):
            con = await Connection.connect('0.1.2.3:999')
    finally:
        if con:
            assert con.connect_params()['endpoint'] == "42.42.42.42:4242"
            await con.close()
