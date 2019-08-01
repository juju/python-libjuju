"""
This example:

1. Connects to the current model
2. Deploys a charm and waits until it reports itself active
3. Creates an offer
4. Lists the offer
3. Destroys the unit and application

"""
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
        model_1 = await controller.add_model('test-cmr-1')
        model_2 = await controller.add_model('test-cmr-2')

        print('Deploying mysql')
        application_1 = await model_1.deploy(
            'cs:mysql-58',
            application_name='mysql',
            series='xenial',
            channel='stable',
        )

        print('Waiting for active')
        await model_1.block_until(
            lambda: all(unit.workload_status == 'active'
                        for unit in application_1.units))

        print('Adding offer')
        await model_1.create_offer("mysql:db")

        offers = await model_1.list_offers()
        await model_1.block_until(
            lambda: all(offer.application_name == 'mysql'
                        for offer in offers.results))

        print('Show offers', ', '.join("%s: %s" % item for offer in offers.results for item in vars(offer).items()))

        print('Deploying wordpress')
        application_2 = await model_2.deploy(
            'cs:trusty/wordpress-5',
            application_name='wordpress',
            series='xenial',
            channel='stable',
        )

        def check():
            for unit in application_2.units:
                if unit.agent_status == 'executing':
                    return True
            return False

        print('Waiting for executing')
        await model_2.block_until(check)

        await model_2.add_relation('wordpress', 'admin/test-cmr-1.mysql')

        time.sleep(10)

        print("Remove SAAS")
        await model_2.remove_saas("mysql")

        print('Removing offer')
        await model_1.remove_offer("admin/test-cmr-1.mysql", force=True)

        print('Destroying models')
        await controller.destroy_model(model_1.info.uuid)
        await controller.destroy_model(model_2.info.uuid)

    except Exception:
        log.exception("Example failed!")
        raise

    finally:
        print('Disconnecting from controller')
        await controller.disconnect()


if __name__ == '__main__':
    loop.run(main())
