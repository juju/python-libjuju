import pytest

from .. import base
from juju.errors import JujuAPIError, JujuError


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


@base.bootstrapped
@pytest.mark.asyncio
async def test_subordinate_charm_zero_units(event_loop):
    # normally in pylibjuju deploy num_units defaults to 1, we switch
    # that to 0 behind the scenes if we see that the charmhub charm
    # we're deploying is a subordinate charm
    async with base.CleanModel() as model:

        # rsyslog-forwarder-ha is a subordinate charm
        app = await model.deploy('rsyslog-forwarder-ha')
        assert len(app.units) == 0
        await app.destroy()

        # note that it'll error if the user tries to use num_units
        with pytest.raises(JujuError):
            await model.deploy('rsyslog-forwarder-ha', num_units=175)

        # (full disclosure: it'll quitely switch to 0 if user enters
        # num_units=1)
        app2 = await model.deploy('rsyslog-forwarder-ha', num_units=1)
        assert len(app2.units) == 0
