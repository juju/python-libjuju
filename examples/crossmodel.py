"""
This example:

1. Connects to the current model
2. Deploys a charm and waits until it reports itself active
3. Creates an offer
4. Lists the offer
3. Destroys the unit and application

"""
import tempfile
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
        application = await offering_model.deploy(
            'mysql',
            application_name='mysql',
            series='trusty',
            channel='stable',
        )

        print('Waiting for active')
        await offering_model.block_until(
            lambda: all(unit.workload_status == 'active'
                        for unit in application.units))

        print('Adding offer')
        await offering_model.create_offer("mysql:db")

        offers = await offering_model.list_offers()
        print('Show offers', ', '.join("%s: %s" % item for offer in offers.results for item in vars(offer).items()))

        print('Consuming offer')
        await consuming_model.consume("admin/test-cmr-1.mysql")

        print('Exporting bundle')
        with tempfile.TemporaryDirectory() as dirpath:
            await offering_model.export_bundle("{}/bundle.yaml".format(dirpath))

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
