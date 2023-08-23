# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from juju import jasyncio
from juju.model import Model

import hvac


async def main():
    """This is a complete example that deploys vault, uses a
    vault client to initialize it, and registers the backend.
    """

    m = Model()
    await m.connect()

    # # deploy postgresql
    await m.deploy('postgresql', series="focal")
    # # deploy vault
    await m.deploy("vault", series="focal")
    # # relate/integrate
    await m.integrate("vault:db", "postgresql:db")
    # # wait for the
    await m.wait_for_idle(["postgresql", "vault"])
    # # expose vault
    vault_app = m.applications["vault"]
    await vault_app.expose()

    # Get a vault client
    # Deploy this entire thing
    status = await m.get_status()
    target = ""
    for unit in status.applications['vault'].units.values():
        target = unit.public_address

    vault_url = "http://%s:8200" % target
    vault_client = hvac.Client(url=vault_url)

    # Initialize vault
    keys = vault_client.sys.initialize(3, 2)
    print(keys)

    # Unseal vault
    vault_client.sys.submit_unseal_keys(keys["keys"])

    target_unit = m.applications['vault'].units[0]
    action = await target_unit.run_action("authorize-charm", token=keys["root_token"])
    await action.wait()

    # Add the secret backend
    c = await m.get_controller()
    response = await c.add_secret_backends("1111", "examplevault", "vault", {"endpoint": vault_url, "token": keys["root_token"]})
    print("Output from add secret backends")
    print(response["results"])

    # List the secrets backend
    list = await c.list_secret_backends()
    print("Output from list secret backends")
    print(list["results"])

    # Remove it
    await c.remove_secret_backends("examplevault")

    # # Finally after removing
    list = await c.list_secret_backends()
    print("Output from list secret backends after removal")
    print(list["results"])

    await m.disconnect()


if __name__ == '__main__':
    jasyncio.run(main())
