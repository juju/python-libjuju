import tempfile
from pathlib import Path

import pytest

from .. import base
from juju import jasyncio


@base.bootstrapped
@pytest.mark.asyncio
async def test_offer(event_loop):
    async with base.CleanModel() as model:
        await model.deploy(
            'cs:~jameinel/ubuntu-lite-7',
            application_name='ubuntu',
            series='focal',
            channel='stable',
        )
        assert 'ubuntu' in model.applications
        await model.wait_for_idle(status="active")
        await model.create_offer("ubuntu:ubuntu")

        offers = await model.list_offers()
        await model.block_until(
            lambda: all(offer.application_name == 'ubuntu'
                        for offer in offers.results))
        await model.remove_offer("admin/{}.ubuntu".format(model.name), force=True)


@base.bootstrapped
@pytest.mark.asyncio
async def test_consume(event_loop):
    async with base.CleanModel() as model_1:
        await model_1.deploy(
            'cs:~jameinel/ubuntu-lite-7',
            application_name='ubuntu',
            series='focal',
            channel='stable',
        )
        assert 'ubuntu' in model_1.applications
        await model_1.wait_for_idle(status="active")
        await model_1.create_offer("ubuntu:ubuntu")

        offers = await model_1.list_offers()
        await model_1.block_until(
            lambda: all(offer.application_name == 'ubuntu'
                        for offer in offers.results))

        # farm off a new model to test the consumption
        async with base.CleanModel() as model_2:
            await model_2.consume("admin/{}.ubuntu".format(model_1.name))

            status = await model_2.get_status()
            if 'ubuntu' not in status.remote_applications:
                raise Exception("Expected ubuntu in saas")

        await model_1.remove_offer("admin/{}.ubuntu".format(model_1.name), force=True)


@base.bootstrapped
@pytest.mark.asyncio
async def test_remove_saas(event_loop):
    async with base.CleanModel() as model_1:
        await model_1.deploy(
            'cs:~jameinel/ubuntu-lite-7',
            application_name='ubuntu',
            series='focal',
            channel='stable',
        )
        assert 'ubuntu' in model_1.applications
        await model_1.wait_for_idle(status="active")
        await model_1.create_offer("ubuntu:ubuntu")

        offers = await model_1.list_offers()
        await model_1.block_until(
            lambda: all(offer.application_name == 'ubuntu'
                        for offer in offers.results))

        # farm off a new model to test the consumption
        async with base.CleanModel() as model_2:
            await model_2.consume("admin/{}.ubuntu".format(model_1.name))

            await model_2.remove_saas('ubuntu')
            await jasyncio.sleep(5)

            status = await model_2.get_status()
            if 'ubuntu' in status.remote_applications:
                raise Exception("Expected ubuntu not to be in saas")

        await model_1.remove_offer("admin/{}.ubuntu".format(model_1.name), force=True)


@base.bootstrapped
@pytest.mark.asyncio
async def test_relate_with_offer(event_loop):
    pytest.skip('Revise: intermittent problem with the remove_saas call')
    async with base.CleanModel() as model_1:
        application = await model_1.deploy(
            'ch:mysql',
            application_name='mysql',
            series='xenial',
            channel='stable',
        )
        assert 'mysql' in model_1.applications
        await model_1.wait_for_idle(status="active")
        await model_1.create_offer("mysql:db")

        offers = await model_1.list_offers()
        await model_1.block_until(
            lambda: all(offer.application_name == 'mysql'
                        for offer in offers.results))

        # farm off a new model to test the consumption
        async with base.CleanModel() as model_2:
            await model_2.deploy(
                'ch:mediawiki',
                application_name='mediawiki',
                series='trusty',
                channel='stable',
            )
            await model_2.block_until(
                lambda: all(unit.agent_status == 'idle'
                            for unit in application.units))

            await model_2.relate("mediawiki:db", "admin/{}.mysql".format(model_1.name))
            status = await model_2.get_status()
            if 'mysql' not in status.remote_applications:
                raise Exception("Expected mysql in saas")

            await model_2.remove_saas('mysql')
            await jasyncio.sleep(5)

            status = await model_2.get_status()
            if 'mysql' in status.remote_applications:
                raise Exception("Expected mysql not to be in saas")

        await model_1.remove_offer("admin/{}.mysql".format(model_1.name), force=True)


@base.bootstrapped
@pytest.mark.asyncio
async def test_add_bundle(event_loop):
    tests_dir = Path(__file__).absolute().parent
    bundle_path = tests_dir / 'bundle'
    cmr_bundle_path = str(bundle_path / 'cmr-bundle.yaml')

    file_contents = None
    try:
        with open(cmr_bundle_path, "r") as file:
            file_contents = file.read()
    except IOError:
        raise

    async with base.CleanModel() as model_1:
        tmp_path = None
        wait_for_min = 5

        with tempfile.TemporaryDirectory() as dirpath:
            try:
                tmp_path = str(Path(dirpath) / 'bundle.yaml')
                with open(tmp_path, "w") as file:
                    file.write(file_contents.format(model_1.name))
            except IOError:
                raise

            await model_1.deploy(
                'influxdb',
                application_name='influxdb',
                channel='stable',
            )
            assert 'influxdb' in model_1.applications
            await model_1.wait_for_idle(status="active")

            await model_1.create_offer("influxdb:grafana-source")

            offers = await model_1.list_offers()

            await model_1.block_until(
                lambda: all(offer.application_name == 'influxdb'
                            for offer in offers.results),
                timeout=60 * wait_for_min)

            # farm off a new model to test the consumption
            async with base.CleanModel() as model_2:
                await model_2.deploy('local:{}'.format(tmp_path))
                await model_2.wait_for_idle(status="active")

            await model_1.remove_offer("admin/{}.influxdb".format(model_1.name), force=True)
