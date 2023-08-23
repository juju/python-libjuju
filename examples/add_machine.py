#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
This example:

1. Connects to the current model
2. Creates two machines and a lxd container
3. Deploys charm to the lxd container

"""
import logging

from juju import jasyncio
from juju.model import Model

MB = 1
GB = 1024


async def main():
    model = Model()
    await model.connect()

    try:
        # add a new default machine
        machine1 = await model.add_machine()
        # add a machine with constraints, disks, and series
        machine2 = await model.add_machine(
            constraints={
                'mem': 256 * MB,
            },
            disks=[{
                'size': 10 * GB,
                'count': 1,
            }],
            series='jammy',
        )

        # add a lxd container to machine2
        machine3 = await model.add_machine(
            'lxd:{}'.format(machine2.id),
            series='jammy'
        )

        # deploy charm to the lxd container
        application = await model.deploy(
            'ch:ubuntu',
            application_name='ubuntu',
            series='jammy',
            channel='stable',
            to=machine3.id
        )

        await model.wait_for_idle(status='active')

        await application.remove()

        await machine3.destroy(force=True)
        await machine2.destroy(force=True)
        await machine1.destroy(force=True)
    finally:
        await model.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)

    jasyncio.run(main())
