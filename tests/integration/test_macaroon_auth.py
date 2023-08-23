# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import logging
import subprocess
import os

import macaroonbakery.bakery as bakery
import macaroonbakery.httpbakery as httpbakery
import macaroonbakery.httpbakery.agent as agent
from juju.errors import JujuAPIError
from juju.model import Model
from juju.client.jujudata import FileJujuData
from juju.controller import Controller

import pytest

from .. import base

log = logging.getLogger(__name__)


# this test must be run serially because it modifies the login password
@base.bootstrapped
@pytest.mark.serial
@pytest.mark.skip('one of old macaroon_auth tests, needs to be revised')
async def test_macaroon_auth_serial(event_loop):
    jujudata = FileJujuData()
    account = jujudata.accounts()[jujudata.current_controller()]
    with base.patch_file('~/.local/share/juju/accounts.yaml'):
        if 'password' in account:
            # force macaroon auth by "changing" password to current password
            result = subprocess.run(
                ['juju', 'change-user-password'],
                input='{0}\n{0}\n'.format(account['password']),
                universal_newlines=True,
                stderr=subprocess.PIPE)
            assert result.returncode == 0, ('Failed to change password: '
                                            '{}'.format(result.stderr))
        controller = Controller()
        try:
            await controller.connect()
            assert controller.is_connected()
        finally:
            if controller.is_connected():
                await controller.disconnect()
        async with base.CleanModel():
            pass  # create and login to model works


@base.bootstrapped
# @pytest.mark.xfail
@pytest.mark.skip('one of old macaroon_auth tests, needs to be revised')
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
# @pytest.mark.xfail
@pytest.mark.skip('one of old macaroon_auth tests, needs to be revised')
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
# @pytest.mark.xfail
@pytest.mark.skip('one of old macaroon_auth tests, needs to be revised')
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
