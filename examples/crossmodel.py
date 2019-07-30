"""
This example:

1. Connects to the current model
2. Deploys a charm and waits until it reports itself active
3. Creates an offer
4. Lists the offer
3. Destroys the unit and application

"""
import time

from juju import loop
from juju.controller import Controller
from juju.model import Model


async def main():
    controller = Controller()
    print("Connecting to controller")
    await controller.connect()

    print('Creating models')
    model_1 = await controller.add_model('test-cmr-1')
    model_2 = await controller.add_model('test-cmr-2')

    try:
        print('Deploying mysql')
        application = await model_1.deploy(
            'mysql',
            application_name='mysql',
            series='trusty',
            channel='stable',
        )

        print('Waiting for active')
        await model_1.block_until(
            lambda: all(unit.workload_status == 'active'
                        for unit in application.units))

        print('Adding offer')
        await model_1.create_offer("mysql:db")

        offers = await model_1.list_offers()
        await model_1.block_until(
            lambda: all(offer.application_name == 'mysql'
                        for offer in offers))

        print('Show offers', ', '.join("%s: %s" % item for offer in offers for item in vars(offer).items()))

        print('Consuming offer')
        await model_2.consume("admin/test-cmr-1.mysql")

        time.sleep(20)

        print('Removing offer')
        await model_1.remove_offer("admin/test-cmr-1.mysql", force=True)
    finally:
        print('Disconnecting from controller')
        await controller.destroy_model(model_1.info.uuid)
        await controller.destroy_model(model_2.info.uuid)
        await controller.disconnect()


if __name__ == '__main__':
    loop.run(main())
