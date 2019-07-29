import pytest

from .. import base


@base.bootstrapped
@pytest.mark.asyncio
async def test_offer(event_loop):
    async with base.CleanModel() as model:
        application = await model.deploy(
            'cs:~jameinel/ubuntu-lite-7',
            application_name='ubuntu',
            series='bionic',
            channel='stable',
        )
        assert 'ubuntu' in model.applications
        await model.block_until(
            lambda: all(unit.workload_status == 'active'
                        for unit in application.units))
        await model.create_offer("ubuntu:ubuntu")

        offers = await model.list_offers()
        await model.block_until(
            lambda: all(offer.application_name == 'ubuntu'
                        for offer in offers))
        await model.remove_offer("admin/{}.ubuntu".format(model.info.name), force=True)
