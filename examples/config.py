# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
This example:

1. Connects to the current model
2. Resets it
3. Deploys a charm and prints its config and constraints

"""
import logging

from juju.model import Model
from juju import jasyncio

log = logging.getLogger(__name__)

MB = 1


async def main():
    model = Model()
    # connect to current model with current user, per Juju CLI
    await model.connect()

    ubuntu_app = await model.deploy(
        'mysql',
        application_name='mysql',
        series='jammy',
        channel='edge',
        config={
            'cluster-name': 'foo',
        },
        constraints={
            'mem': 256 * MB,
        },
    )
    await model.wait_for_idle(status='active')

    # update and check app config
    await ubuntu_app.set_config({'cluster-name': 'bar'})
    config = await ubuntu_app.get_config()
    assert (config['cluster-name']['value'] == 'bar')

    # update and check app constraints
    await ubuntu_app.set_constraints({'mem': 512 * MB})
    constraints = await ubuntu_app.get_constraints()
    assert (constraints['mem'] == 512 * MB)

    print('Removing mysql')
    await ubuntu_app.remove()

    print('Disconnecting from model')
    await model.disconnect()


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)
    jasyncio.run(main())
