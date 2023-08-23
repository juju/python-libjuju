# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from juju import jasyncio
from juju.model import Model


async def main():

    m = Model()
    await m.connect()

    secrets = await m.list_secrets()
    print(secrets)
    await m.disconnect()


if __name__ == '__main__':
    jasyncio.run(main())
