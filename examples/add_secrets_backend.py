from juju import jasyncio
from juju.model import Model

import hvac


async def main():
    """This is a complete example that deploys vault, uses a
    vault client to initialize it, and registers the backend.
    """

    m = Model()
    await m.connect_current()

    # deploy postgresql
    await m.deploy('postgresql')
    # deploy vault
    await m.deploy("vault", series="focal")
    # relate/integrate
    await m.relate("vault:db", "postgresql:db")
    # wait for the
    await m.wait_for_idle(["vault"])
    # expose vault
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

    # Unseal vault
    vault_client.sys.submit_unseal_keys(keys["keys"])

    # Add the secret backend
    c = await m.get_controller()
    response = await c.add_secret_backends("1000", "myvault", "vault", {"endpoint": vault_url})
    print("Output from add secret backends")
    print(response["results"])

    # List the secrets backend
    list = await c.list_secret_backends()
    print("Output from list secret backends")
    print(list["results"])

    # Remove it
    await c.remove_secret_backends("myvault")

    # Finally after removing
    list = await c.list_secret_backends()
    print("Output from list secret backends after removal")
    print(list["results"])

    await m.disconnect()


if __name__ == '__main__':
    jasyncio.run(main())
