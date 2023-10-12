from juju import jasyncio
from juju.model import Model


async def main():
    charm = 'juju-qa-test'

    model = Model()
    print('Connecting to model')
    # connect to current model with current user, per Juju CLI
    await model.connect()

    try:
        print(f'Deploying {charm} --channel latest/edge --revision 19')
        application = await model.deploy(
            'juju-qa-test',
            application_name='test',
            channel='latest/edge',
            series='xenial',
            revision=19,
        )

        print('Waiting for active')
        await model.wait_for_idle(status='active')

        print(f'Removing {charm}')
        await application.remove()
    finally:
        print('Disconnecting from model')
        await model.disconnect()


if __name__ == '__main__':
    jasyncio.run(main())
