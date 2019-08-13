"""
This example:

1. Connects to the current controller
2. Creates two models for consuming and offering
2. Deploys a charm and waits until it reports itself active
3. Creates an offer
4. Lists the offer
5. Deploys a charm and adds relation to the offering url
6. Destroys the units and applications

"""
import tempfile
import time
from logging import getLogger

from juju import loop
from juju.controller import Controller

log = getLogger(__name__)


async def main():
    controller = Controller()
    print("Connecting to controller")
    await controller.connect()

    try:
        print('Creating models')
        offering_model = await controller.add_model('test-cmr-1')
        consuming_model = await controller.add_model('test-cmr-2')

        print('Deploying mysql')
        application_1 = await offering_model.deploy(
            'cs:mysql-58',
            application_name='mysql',
            series='xenial',
            channel='stable',
        )

        print('Waiting for active')
        await offering_model.block_until(
            lambda: all(unit.workload_status == 'active'
                        for unit in application_1.units))

        print('Adding offer')
        await offering_model.create_offer("mysql:db")

        offers = await offering_model.list_offers()
        await offering_model.block_until(
            lambda: all(offer.application_name == 'mysql'
                        for offer in offers.results))

        print('Show offers', ', '.join("%s: %s" % item for offer in offers.results for item in vars(offer).items()))

        print('Deploying wordpress')
        application_2 = await consuming_model.deploy(
            'cs:trusty/wordpress-5',
            application_name='wordpress',
            series='xenial',
            channel='stable',
        )

        print('Waiting for executing')
        await consuming_model.block_until(
            lambda: all(unit.agent_status == 'executing'
                        for unit in application_2.units))

        await consuming_model.add_relation('wordpress', 'admin/test-cmr-1.mysql')

        print('Exporting bundle')
        with tempfile.TemporaryDirectory() as dirpath:
            await offering_model.export_bundle("{}/bundle.yaml".format(dirpath))

        time.sleep(10)

        print("Remove SAAS")
        await consuming_model.remove_saas("mysql")

        print('Removing offer')
        await offering_model.remove_offer("admin/test-cmr-1.mysql", force=True)

        print('Destroying models')
        await controller.destroy_model(offering_model.info.uuid)
        await controller.destroy_model(consuming_model.info.uuid)

    except Exception:
        log.exception("Example failed!")
        raise

    finally:
        print('Disconnecting from controller')
        await controller.disconnect()


if __name__ == '__main__':
    loop.run(main())
