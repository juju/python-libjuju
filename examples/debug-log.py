# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""
This example demonstrate how debug-log works

"""
from juju import jasyncio
from juju.model import Model


async def main():
    model = Model()
    await model.connect_current()

    await model.debug_log(
        # limit=15,
        # exclude_module=['juju.worker.logforwarder'],
        # include_module=['juju.worker.dependency'], # <- only log dependency module
        # include=['machine-0'], # <- only log from machine-0
        # exclude=['machine-0'], # <- no log from machine-0
        # level='WARNING',
    )

    application = await model.deploy(
        'ch:ubuntu',
        application_name='ubuntu',
        series='trusty',
        channel='stable',
    )

    await model.wait_for_idle(status='active')

    await application.remove()
    await model.disconnect()


if __name__ == '__main__':
    jasyncio.run(main())
