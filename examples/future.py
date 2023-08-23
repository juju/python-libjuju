# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
This example doesn't work - it demonstrates features that don't exist yet.

"""
import logging

from juju.model import Model
from juju import jasyncio


async def main():
    model = Model()
    # connect to current model with current user, per Juju CLI
    await model.connect()

    goal_state = Model.from_yaml('bundle-like-thing')
    ubuntu_app = await model.deploy(
        'ch:ubuntu',
        application_name='ubuntu',
        series='trusty',
        channel='stable',
    )
    ubuntu_app.on_unit_added(callback=lambda unit: True)

    await model.deploy(
        'ch:nrpe',
        application_name='nrpe',
        series='trusty',
        channel='stable',
        num_units=0,
    )
    await model.relate(
        'ubuntu',
        'nrpe',
    )

    result, ok = await model.block_until(
        lambda: model.matches(goal_state),
        timeout=600
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)
    jasyncio.run(main())
