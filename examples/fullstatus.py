from juju import loop
from juju.model import Model


async def status():
    model = Model()
    await model.connect()

    status = await model.get_status()
    await model.disconnect()

    print('Applications:', list(status.applications.keys()))
    print('Machines:', list(status.machines.keys()))
    print('Relations:', status.relations)

    return status


if __name__ == '__main__':
    loop.run(status())
