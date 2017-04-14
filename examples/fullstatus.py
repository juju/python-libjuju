import asyncio

from juju.client.connection import Connection
from juju.client.client import ClientFacade
from juju import loop

async def status():
    conn = await Connection.connect_current()
    client = ClientFacade.from_connection(conn)

    patterns = None
    status = await client.FullStatus(patterns)
    await conn.close()

    print('Applications:', list(status.applications.keys()))
    print('Machines:', list(status.machines.keys()))
    print('Relations:', status.relations)

    return status

if __name__ == '__main__':
    loop.run(status())

