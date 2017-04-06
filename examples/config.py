"""
This example:

1. Connects to the current model
2. Resets it
3. Deploys a charm and prints its config and constraints

"""
import asyncio
import logging

from juju.model import Model
from juju import loop

log = logging.getLogger(__name__)

MB = 1


async def main():
    model = Model()
    await model.connect_current()
    await model.reset(force=True)

    ubuntu_app = await model.deploy(
        'mysql',
        application_name='mysql',
        series='trusty',
        channel='stable',
        config={
            'tuning-level': 'safest',
        },
        constraints={
            'mem': 256 * MB,
        },
    )

    # update and check app config
    await ubuntu_app.set_config({'tuning-level': 'fast'})
    config = await ubuntu_app.get_config()
    assert(config['tuning-level']['value'] == 'fast')

    # update and check app constraints
    await ubuntu_app.set_constraints({'mem': 512 * MB})
    constraints = await ubuntu_app.get_constraints()
    assert(constraints['mem'] == 512 * MB)

    await model.disconnect()

    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)
    loop.run(main())
