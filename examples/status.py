"""
This example demonstrate how status works

"""
from juju import jasyncio
import logging
import sys
from logging import getLogger
from juju.model import Model
from juju.status import formatted_status

LOG = getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


async def main():
    model = Model()
    await model.connect_current()

    application = await model.deploy(
        'cs:ubuntu-10',
        application_name='ubuntu',
        series='trusty',
        channel='stable',
    )
    await jasyncio.sleep(10)
    # Print the status to observe the evolution
    # during a minute
    for i in range(12):
        try:
            # By setting raw to True, the returned
            # entry contains a FullStatus object with
            # all the available status data.
            # status = await model.status(raw=True)
            status = await formatted_status(model)
            print(status)
        except Exception as e:
            print(e)
        await jasyncio.sleep(5)

    await application.remove()
    await model.disconnect()

if __name__ == '__main__':
    jasyncio.run(main())
