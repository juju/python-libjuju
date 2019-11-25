"""
This example shows how to reconnect to a model if you encounter an error

1. Connects to current model.
2. Attempts to get an application that doesn't exist.
3. Disconnect then reconnect.

"""
from juju import loop
from juju.model import Model
from juju.errors import JujuEntityNotFoundError


async def main():
    model = Model()

    retryCount = 3
    for i in range(0, retryCount):
        await model.connect_current()
        try:
            model.applications['foo'].relations
        except JujuEntityNotFoundError as e:
            print(e.entity_name)
        finally:
            await model.disconnect()
        # Everything worked out, continue on wards.


if __name__ == '__main__':
    loop.run(main())
