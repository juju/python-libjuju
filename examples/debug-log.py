"""
This example demonstrate how debug-log works

"""
import asyncio
from juju import loop
import logging
import sys
from logging import getLogger
from juju.model import Model

LOG = getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


async def main():
    model = Model()
    await model.connect_current()

    await model.debug_log()

    application = await model.deploy(
        'cs:ubuntu-10',
        application_name='ubuntu',
        series='trusty',
        channel='stable',
    )

    await asyncio.sleep(10)
    await model.wait_for_idle(status='active')

    await application.remove()
    await model.disconnect()

if __name__ == '__main__':
    loop.run(main())
