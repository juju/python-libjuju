import asyncio

from juju.client.connection import Connection
from juju.client.client import ClientFacade


loop = asyncio.get_event_loop()
conn = loop.run_until_complete(Connection.connect_current())


async def status():
    client = ClientFacade()
    client.connect(conn)

    patterns = None
    status = await client.FullStatus(patterns)
    await conn.close()

    print('Applications:', list(status.applications.keys()))
    print('Machines:', list(status.machines.keys()))
    print('Relations:', status.relations)

    return status

loop.run_until_complete(status())
loop.stop()
