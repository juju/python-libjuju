"""
This is a very basic example that connects to the currently selected model
and prints the number of applications deployed to it.

Then attempts to use scp to grab the profile, as a way to show how scp works
from a pylibjuju perspective.
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
        print('There are {} applications'.format(len(model.applications)))

        machine = model.machines['0']
        # This roughly expands to the following:
        # scp -i ~/.local/share/juju/ssh/juju_id_rsa -o StrictHostKeyChecking=no -q -B ubuntu@10.132.183.88:/home/ubuntu/.profile /tmp/profile
        await machine.scp_from("/home/ubuntu/.profile", "/tmp/profile")
    finally:
        if model.is_connected():
            print('Disconnecting from model')
            await model.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop.run(main())
