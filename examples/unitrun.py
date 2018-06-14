"""
This example:

1. Connects to current model and resets it.
2. Deploys one ubuntu unit.
3. Runs an action against the unit.
4. Waits for the action results to come back, then exits.

"""
import logging

from juju.model import Model
from juju import loop


async def run_command(unit):
    logging.debug('Running command on unit %s', unit.name)

    # unit.run() returns a juju.action.Action instance
    action = await unit.run('unit-get public-address')
    logging.debug("Action results: %s", action.results)


async def main():
    model = Model()
    # connect to current model with current user, per Juju CLI
    await model.connect()

    app = await model.deploy(
        'ubuntu-0',
        application_name='ubuntu',
        series='trusty',
        channel='stable',
    )

    for unit in app.units:
        await run_command(unit)

    await model.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)
    loop.run(main())
