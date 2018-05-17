import logging
import os

import macaroonbakery.bakery as bakery
import macaroonbakery.httpbakery as httpbakery
import macaroonbakery.httpbakery.agent as agent
from juju.errors import JujuAPIError
from juju.model import Model

import pytest

from .. import base

log = logging.getLogger(__name__)


@base.bootstrapped
@pytest.mark.asyncio
@pytest.mark.xfail
async def test_macaroon_auth(event_loop):
    auth_info, username = agent_auth_info()
    # Create a bakery client that can do agent authentication.
    client = httpbakery.Client(
        key=auth_info.key,
        interaction_methods=[agent.AgentInteractor(auth_info)],
    )

    async with base.CleanModel(bakery_client=client) as m:
        async with await m.get_controller() as c:
            await c.grant_model(username, m.info.uuid, 'admin')
        async with Model(
            jujudata=NoAccountsJujuData(m._connector.jujudata),
            bakery_client=client,
        ):
            pass


@base.bootstrapped
@pytest.mark.asyncio
@pytest.mark.xfail
async def test_macaroon_auth_with_bad_key(event_loop):
    auth_info, username = agent_auth_info()
    # Use a random key rather than the correct key.
    auth_info = auth_info._replace(key=bakery.generate_key())
    # Create a bakery client can do agent authentication.
    client = httpbakery.Client(
        key=auth_info.key,
        interaction_methods=[agent.AgentInteractor(auth_info)],
    )

    async with base.CleanModel(bakery_client=client) as m:
        async with await m.get_controller() as c:
            await c.grant_model(username, m.info.uuid, 'admin')
        try:
            async with Model(
                jujudata=NoAccountsJujuData(m._connector.jujudata),
                bakery_client=client,
            ):
                pytest.fail('Should not be able to connect with invalid key')
        except httpbakery.BakeryException:
            # We're expecting this because we're using the
            # wrong key.
            pass


@base.bootstrapped
@pytest.mark.asyncio
async def test_macaroon_auth_with_unauthorized_user(event_loop):
    auth_info, username = agent_auth_info()
    # Create a bakery client can do agent authentication.
    client = httpbakery.Client(
        key=auth_info.key,
        interaction_methods=[agent.AgentInteractor(auth_info)],
    )
    async with base.CleanModel(bakery_client=client) as m:
        # Note: no grant of rights to the agent user.
        try:
            async with Model(
                jujudata=NoAccountsJujuData(m._connector.jujudata),
                bakery_client=client,
            ):
                pytest.fail('Should not be able to connect without grant')
        except (JujuAPIError, httpbakery.DischargeError):
            # We're expecting this because we're using the
            # wrong user name.
            pass


def agent_auth_info():
    agent_data = os.environ.get('TEST_AGENTS')
    if agent_data is None:
        pytest.skip('skipping macaroon_auth because no TEST_AGENTS '
                    'environment variable is set')
    auth_info = agent.read_auth_info(agent_data)
    if len(auth_info.agents) != 1:
        raise Exception('TEST_AGENTS agent data requires exactly one agent')
    return auth_info, auth_info.agents[0].username


class NoAccountsJujuData:
    def __init__(self, jujudata):
        self.__jujudata = jujudata

    def __getattr__(self, name):
        return getattr(self.__jujudata, name)

    def accounts(self):
        return {}
