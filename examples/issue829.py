"""
This example:

1. Connects to the current model
2. Deploy a charm and waits until it reports itself active
3. Destroys the unit and application

"""

from juju.model import Model
from juju.errors import JujuError
import asyncio


async def errorlu():
    raise JujuError("HOP")


async def iki():
    return await errorlu()


async def juju_stats():
    m = Model()
    await m.connect()
    await m.disconnect()


try:
    asyncio.run(juju_stats())
except JujuError:
    print("Error handled")
