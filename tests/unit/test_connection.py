import asyncio
import json
import mock
import pytest
from collections import deque

from websockets.exceptions import ConnectionClosed

from .. import base
from juju.client.connection import Connection


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
    con = Connection(*[None]*4)
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
    con._get_sll = mock.MagicMock()
    try:
        with mock.patch('websockets.connect', base.AsyncMock(return_value=ws)):
            await con.open()
        actual_responses = []
        for i in range(3):
            actual_responses.append(await con.rpc({'version': 1}))
        assert actual_responses == expected_responses
    finally:
        await con.close()
