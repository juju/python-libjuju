import pytest

from .. import base
from juju.errors import JujuAPIError


@base.bootstrapped
@pytest.mark.asyncio
async def test_info(event_loop):
    async with base.CleanModel() as model:
        result = await model.charmhub.info("hello-juju")

        assert result.result.name == "hello-juju"


@base.bootstrapped
@pytest.mark.asyncio
async def test_info_with_channel(event_loop):
    async with base.CleanModel() as model:
        result = await model.charmhub.info("hello-juju", "latest/stable")

        assert result.result.name == "hello-juju"
        assert "latest/stable" in result.result.channel_map


@base.bootstrapped
@pytest.mark.asyncio
async def test_info_not_found(event_loop):
    async with base.CleanModel() as model:
        try:
            await model.charmhub.info("badnameforapp")
        except JujuAPIError as e:
            assert e.message == "badnameforapp not found"
        else:
            assert False


@base.bootstrapped
@pytest.mark.asyncio
async def test_find(event_loop):
    async with base.CleanModel() as model:
        result = await model.charmhub.find("kube")

        assert len(result.result) > 0
        for resp in result.result:
            assert resp.name != ""
            assert resp.type_ in ["charm", "bundle"]


@base.bootstrapped
@pytest.mark.asyncio
async def test_find_bundles(event_loop):
    async with base.CleanModel() as model:
        result = await model.charmhub.find("kube", charm_type="bundle")

        assert len(result.result) > 0
        for resp in result.result:
            assert resp.name != ""
            assert resp.type_ in ["bundle"]


@base.bootstrapped
@pytest.mark.asyncio
async def test_find_all(event_loop):
    async with base.CleanModel() as model:
        result = await model.charmhub.find("")

        assert len(result.result) > 0
        for resp in result.result:
            assert resp.name != ""
            assert resp.type_ in ["charm", "bundle"]
