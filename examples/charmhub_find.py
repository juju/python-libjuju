"""
Example to show how to connect to the current model and search the charm-hub
repository for charms.
"""
import logging

from juju import loop
from juju.model import Model

log = logging.getLogger(__name__)


async def main():
    model = Model()
    try:
        # connect to the current model with the current user, per the Juju CLI
        await model.connect()

        # do a partial query so that we get more results.
        charms = await model.charmhub.find("kuber")

        print("Bundle\tName")
        for resp in charms.result:
            print("{}\t{}".format("N" if resp.type_ == "charm" else "Y", resp.name))
    finally:
        if model.is_connected():
            print('Disconnecting from model')
            await model.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop.run(main())
