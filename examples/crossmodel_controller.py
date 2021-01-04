"""
This example:

1. Connects to test and test2 controllers
2. Creates models on each controllers
3. Deploys a charm and waits until it reports itself active
4. Creates an offer
5. Lists the offer
6. Consumes the offer
7. Exports the bundle
8. Removes the SAAS
9. Removes the offer
10. Destroys models and disconnects
"""
import tempfile
from logging import getLogger

from juju import loop
from juju.controller import Controller

log = getLogger(__name__)


async def main():
    controller1 = Controller()
    print("Connecting to controller")
    await controller1.connect("test")

    controller2 = Controller()
    print("Connecting to controller")
    await controller2.connect("test2")

    try:
        print('Creating models')
        offering_model = await controller1.add_model('test-cmr-1')
        consuming_model = await controller2.add_model('test-cmr-2')

        print('Deploying mysql')
        application = await offering_model.deploy(
            'cs:mysql',
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
        await consuming_model.consume("admin/test-cmr-1.mysql", controller_name="test")

        print('Exporting bundle')
        with tempfile.TemporaryDirectory() as dirpath:
            await offering_model.export_bundle("{}/bundle.yaml".format(dirpath))

        print("Remove SAAS")
        await consuming_model.remove_saas("mysql")

        print('Removing offer')
        await offering_model.remove_offer("admin/test-cmr-1.mysql", force=True)

        print('Destroying models')
        await controller1.destroy_model(offering_model.info.uuid)
        await controller2.destroy_model(consuming_model.info.uuid)

    except Exception:
        log.exception("Example failed!")
        raise

    finally:
        print('Disconnecting from controller')
        await controller1.disconnect()
        await controller2.disconnect()


if __name__ == '__main__':
    loop.run(main())
