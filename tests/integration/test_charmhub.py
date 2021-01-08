import pytest

from .. import base
from juju.errors import JujuAPIError


@base.bootstrapped
@pytest.mark.asyncio
async def test_info(event_loop):
    async with base.CleanModel() as model:
        result = await model.charmhub.info("mattermost")

        assert result.result.name == "mattermost"


@base.bootstrapped
@pytest.mark.asyncio
async def test_info_with_channel(event_loop):
    async with base.CleanModel() as model:
        result = await model.charmhub.info("mattermost", "latest/stable")

        assert result.result.name == "mattermost"
        assert "latest/stable" in result.result.channel_map


@base.bootstrapped
@pytest.mark.asyncio
async def test_info_not_found(event_loop):
    async with base.CleanModel() as model:
        try:
            await model.charmhub.info("badnameforapp")
        except JujuAPIError as e:
            assert e.message == "No charm or bundle with name 'badnameforapp'."
        else:
            raise
