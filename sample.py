import logging

from juju import jasyncio
from juju.client import client
from juju.model import Model


async def main():
    m = Model()
    await m.connect(model_name="testm")
    app_facade = client.ApplicationFacade.from_connection(m.connection())
    sync_facade = client.ApplicationFacade.from_sync_connection(m.sync_connection())
    for app_name in m.applications:
        print()
        # print(m.applications[app_name].constraints.arch)  # temporarily broken, but why?
        print(m.applications[app_name].name)
        print(m.applications[app_name].exposed)
        print(m.applications[app_name].charm_url)
        print(m.applications[app_name].owner_tag)
        # print(m.applications[app_name].life)
        print(m.applications[app_name].min_units)
        print(m.applications[app_name].constraints)
        print(m.applications[app_name].subordinate)
        # print(m.applications[app_name].status)
        print(m.applications[app_name].workload_version)

        print()
        app = await app_facade.Get(app_name)
        print(app.application, app.charm, app.constraints.arch)
        app = sync_facade.sync_Get(app_name)
        print(app.application, app.charm, app.constraints.arch)


class SymbolFilter(logging.Filter):
    DEBUG = '🐛'
    INFO = 'ℹ️'
    WARNING = '⚠️'
    ERROR = '❌'
    CRITICAL = '🔥'

    def filter(self, record):
        record.symbol = getattr(self, record.levelname, '#')
        # FIXME can control log record origin here if needed
        return True


if __name__ == "__main__":
    # FIXME why is level=DEBUG broken?
    logging.basicConfig(level="INFO", format="%(symbol)s %(message)s")
    logging.root.addFilter(SymbolFilter())
    jasyncio.run(main())
