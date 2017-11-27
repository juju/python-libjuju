import asyncio
import json
from collections import deque

import mock
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
