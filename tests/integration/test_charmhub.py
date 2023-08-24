# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import pytest

from .. import base
from juju.errors import JujuError
from juju import jasyncio


@base.bootstrapped
async def test_info(event_loop):
    async with base.CleanModel() as model:
        _, name = await model.charmhub.get_charm_id("ubuntu")
        assert name == "ubuntu"

        charm_name = 'juju-qa-test'
        charm_info = await model.charmhub.info(charm_name)
        assert charm_info['name'] == 'juju-qa-test'
        assert charm_info['type'] == 'charm'
        assert charm_info['id'] == 'Hw30RWzpUBnJLGtO71SX8VDWvd3WrjaJ'
        assert '2.0/stable' in charm_info['channel-map']
        cm_rev = charm_info['channel-map']['2.0/stable']['revision']
        if isinstance(cm_rev, dict):
            # New client (>= 3.0)
            assert cm_rev['revision'] == 22
        else:
            # Old client (<= 2.9)
            assert cm_rev == 22


@base.bootstrapped
async def test_info_with_channel(event_loop):
    async with base.CleanModel() as model:
        charm_info = await model.charmhub.info("juju-qa-test", "2.0/stable")
        assert charm_info['name'] == 'juju-qa-test'
        assert '2.0/stable' in charm_info['channel-map']
        assert 'latest/stable' not in charm_info['channel-map']

        try:
            await model.charmhub.info("juju-qa-test", "non-existing-channel")
        except JujuError as err:
            assert err.message == 'Charmhub.info : channel ' \
                                  'non-existing-channel not found for ' \
                                  'juju-qa-test'
        else:
            assert False, "non-existing-channel didn't raise an error"


@base.bootstrapped
async def test_info_not_found(event_loop):
    async with base.CleanModel() as model:
        with pytest.raises(JujuError) as err:
            await model.charmhub.info("badnameforapp")
            assert "badnameforapp not found" in str(err)


@base.bootstrapped
@pytest.mark.skip('CharmHub facade no longer exists')
async def test_find(event_loop):
    async with base.CleanModel() as model:
        result = await model.charmhub.find("kube")

        assert len(result.result) > 0
        for resp in result.result:
            assert resp.name != ""
            assert resp.type_ in ["charm", "bundle"]


@base.bootstrapped
@pytest.mark.skip('CharmHub facade no longer exists')
async def test_find_bundles(event_loop):
    async with base.CleanModel() as model:
        result = await model.charmhub.find("kube", charm_type="bundle")

        assert len(result.result) > 0
        for resp in result.result:
            assert resp.name != ""
            assert resp.type_ in ["bundle"]


@base.bootstrapped
@pytest.mark.skip('CharmHub facade no longer exists')
async def test_find_all(event_loop):
    async with base.CleanModel() as model:
        result = await model.charmhub.find("")

        assert len(result.result) > 0
        for resp in result.result:
            assert resp.name != ""
            assert resp.type_ in ["charm", "bundle"]


@base.bootstrapped
@pytest.mark.skip('This tries to test juju controller logic')
async def test_subordinate_charm_zero_units(event_loop):
    # normally in pylibjuju deploy num_units defaults to 1, we switch
    # that to 0 behind the scenes if we see that the charmhub charm
    # we're deploying is a subordinate charm
    async with base.CleanModel() as model:

        # rsyslog-forwarder-ha is a subordinate charm
        app = await model.deploy('rsyslog-forwarder-ha')
        await jasyncio.sleep(5)

        assert len(app.units) == 0
        await app.destroy()
        await jasyncio.sleep(5)

        # note that it'll error if the user tries to use num_units
        with pytest.raises(JujuError):
            await model.deploy('rsyslog-forwarder-ha', num_units=175)

        # (full disclosure: it'll quitely switch to 0 if user enters
        # num_units=1, instead of erroring)
        app2 = await model.deploy('rsyslog-forwarder-ha', num_units=1)
        await jasyncio.sleep(5)
        assert len(app2.units) == 0


@base.bootstrapped
async def test_subordinate_false_field_exists(event_loop):
    async with base.CleanModel() as model:
        assert await model.charmhub.is_subordinate("rsyslog-forwarder-ha")
        assert not await model.charmhub.is_subordinate("mysql-innodb-cluster")


@base.bootstrapped
async def test_list_resources(event_loop):
    async with base.CleanModel() as model:
        resources = await model.charmhub.list_resources('hello-kubecon')
        assert isinstance(resources, list) and len(resources) > 0
