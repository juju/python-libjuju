"""
This example:

1. Creates a model on the current controller
2. Deploys a charm to it.
3. Attempts to ssh into the charm

"""
import logging

from juju import loop
from juju.controller import Model

log = logging.getLogger(__name__)


async def main():
    model = Model()
    try:
        await model.connect_current()
        print('There are {} applications'.format(len(model.applications)))
    finally:
        if model.is_connected():
            print('Disconnecting from model')
            await model.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop.run(main())
