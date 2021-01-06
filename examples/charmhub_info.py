"""
Example to show how to connect to the current model and query the charm-hub
repository for information about a given charm.
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

        charm = await model.charmhub.info("mattermost")
        print(charm)
    finally:
        if model.is_connected():
            print('Disconnecting from model')
            await model.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop.run(main())
