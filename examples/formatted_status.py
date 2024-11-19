# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""This example demonstrates how to obtain a formatted full status
description. For a similar solution using the FullStatus object
check examples/fullstatus.py
"""

import logging
import sys
import tempfile
from logging import getLogger

from juju import jasyncio
from juju.model import Model
from juju.status import formatted_status

LOG = getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


async def main():
    model = Model()
    await model.connect_current()

    application = await model.deploy(
        "ch:ubuntu",
        application_name="ubuntu",
        series="trusty",
        channel="stable",
    )

    await jasyncio.sleep(10)
    tmp = tempfile.NamedTemporaryFile(delete=False)  # noqa: SIM115
    LOG.info("status dumped to %s", tmp.name)
    with open(tmp.name, "w") as f:
        for _ in range(10):
            # Uncomment this line to get the full status
            # using the standard output.
            # await formatted_status(model, target=sys.stdout)
            await formatted_status(model, target=f)
            f.write("-----------\n")
            await jasyncio.sleep(1)
    await application.remove()
    await model.disconnect()


if __name__ == "__main__":
    jasyncio.run(main())
