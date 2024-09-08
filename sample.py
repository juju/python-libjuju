from juju import jasyncio
from juju.client import client
from juju.model import Model


async def main():
    m = Model()
    await m.connect(model_name="testm")
    app_facade = client.ApplicationFacade.from_connection(m.connection())
    sync_facade = client.ApplicationFacade.from_sync_connection(m.sync_connection())
    for app_name in m.applications:
        app = await app_facade.Get(app_name)
        print(app.application, app.charm)
        app = sync_facade.sync_Get(app_name)
        print(app.application, app.charm)


if __name__ == "__main__":
    jasyncio.run(main())
