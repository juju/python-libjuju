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
