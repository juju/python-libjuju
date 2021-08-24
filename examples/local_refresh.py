"""
This example:

1. Connects to the current model
2. Upgrades previously deployed ubuntu charm

"""
from juju import loop
from juju.model import Model


async def main():
    model = Model()
    print('Connecting to model')
    # connect to current model with current user, per Juju CLI
    await model.connect()

    try:
        print('Get deployed application')
        app = model.appplications["ubuntu"]

        print('Refresh/Upgrade Ubuntu charm with local charm')
        await app.refresh(path="path/to/local/ubuntu.charm")
    finally:
        print('Disconnecting from model')
        await model.disconnect()


if __name__ == '__main__':
    loop.run(main())
