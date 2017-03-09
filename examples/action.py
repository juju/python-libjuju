"""
This example:

1. Connects to current model and resets it.
2. Deploys a git unit.
3. Runs an action against the unit.
4. Waits for the action results to come back, then exits.

"""
import asyncio
import logging

from juju import loop
from juju.model import Model


async def run_action(unit):
    logging.debug('Running action on unit %s', unit.name)

    # unit.run() returns a juju.action.Action instance
    action = await unit.run_action('add-repo', repo='myrepo')
    # wait for the action to complete
    action = await action.wait()

    logging.debug("Action results: %s", action.results)


async def main():
    model = Model()
    await model.connect_current()
    await model.reset(force=True)

    app = await model.deploy(
        'git',
        application_name='git',
        series='trusty',
        channel='stable',
    )

    for unit in app.units:
        await run_action(unit)

    await model.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)
    loop.run(main())
