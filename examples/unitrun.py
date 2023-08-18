# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
This example:

1. Connects to current model and resets it.
2. Deploys one ubuntu unit.
3. Runs an action against the unit.
4. Waits for the action results to come back, then exits.

"""
import logging

from juju.model import Model
from juju import jasyncio


async def run_command(unit):
    logging.debug('Running command on unit %s', unit.name)
    # unit.run() returns a juju.action.Action instance,
    # it needs to be wait()'ed to get the results
    action = await unit.run('unit-get public-address')
    await action.wait()

    out1 = f"Action status: {action.status}"
    logging.debug(out1)
    print(out1)
    # 'completed'

    out2 = f"Action results: {action.results}"
    logging.debug(out2)
    print(out2)
    # {'return-code': 0, 'stdout': '<IP Addr>\n'}


async def main():
    model = Model()
    # connect to current model with current user, per Juju CLI
    await model.connect()

    app = await model.deploy(
        'ch:ubuntu',
        application_name='ubuntu',
        series='trusty',
        channel='stable',
    )

    for unit in app.units:
        await run_command(unit)

    await app.remove()

    await model.disconnect()


if __name__ == '__main__':
    # Uncomment below to get logging output

    # logging.basicConfig(level=logging.DEBUG)
    # ws_logger = logging.getLogger('websockets.protocol')
    # ws_logger.setLevel(logging.INFO)
    """
    Should see something like the following in the output if using LOGGING

    DEBUG:root:Action status: completed
    DEBUG:root:Action results: {'return-code': 0, 'stdout': '10.42.51.101\n'}
    """
    jasyncio.run(main())
