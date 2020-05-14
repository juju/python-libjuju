#!/usr/bin/env python3.5

"""
This example:

1. Connects to the current model
2. Creates two machines and a lxd container
3. Deploys charm to the lxd container

"""
import logging

from juju import loop
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
                'pool': 'rootfs',
                'size': 10 * GB,
                'count': 1,
            }],
            series='xenial',
        )
        # add a lxd container to machine2
        machine3 = await model.add_machine(
            'lxd:{}'.format(machine2.id),
            series='xenial'
        )

        # deploy charm to the lxd container
        application = await model.deploy(
            'ubuntu-10',
            application_name='ubuntu',
            series='xenial',
            channel='stable',
            to=machine3.id
        )

        await model.block_until(
            lambda: all(unit.workload_status == 'active'
                        for unit in application.units))

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

    loop.run(main())
