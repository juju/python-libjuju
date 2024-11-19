#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""This example shows how to reconnect to a model if you encounter an error

1. Connects to current model.
2. Attempts to get an application that doesn't exist.
3. Disconnect then reconnect.

"""

from juju import jasyncio
from juju.errors import JujuEntityNotFoundError
from juju.model import Model


async def main():
    model = Model()

    retries = 3
    for _ in range(0, retries):
        await model.connect_current()
        try:
            print(model.applications["foo"].relations)
        except JujuEntityNotFoundError as e:
            print(e.entity_name)
        finally:
            await model.disconnect()
        # Everything worked out, continue on wards.


if __name__ == "__main__":
    jasyncio.run(main())
