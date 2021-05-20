"""
This example:

1. Connects to the current model.
2. Deploys a charm and waits until it reports itself active.
3. Demonstrates exposing application endpoints to space and CIDR combinations.
3. Demonstrates unexposing application endpoints.

NOTE: this test must be run against a 2.9 controller.
"""
from juju import loop
from juju.model import Model
from juju.application import ExposedEndpoint


async def main():
    model = Model()
    print('Connecting to model')
    # connect to current model with current user, per Juju CLI
    await model.connect()

    try:
        print('Deploying ubuntu')
        application = await model.deploy(
            'cs:~jameinel/ubuntu-lite-7',
            application_name='ubuntu',
            series='trusty',
            channel='stable',
        )

        print('Waiting for active')
        await model.block_until(
            lambda: all(unit.workload_status == 'active'
                        for unit in application.units))

        print('Expose all opened port ranges')
        await application.expose()

        print('Expose all opened port ranges to the CIDRs that correspond to a list of spaces')
        await application.expose(exposed_endpoints={
            "": ExposedEndpoint(to_spaces=["alpha"])
        })

        print('Expose all opened port ranges to a list of CIDRs')
        await application.expose(exposed_endpoints={
            "": ExposedEndpoint(to_cidrs=["10.0.0.0/24"])
        })

        print('Expose all opened port ranges to a list of spaces and CIDRs')
        await application.expose(exposed_endpoints={
            "": ExposedEndpoint(to_spaces=["alpha"], to_cidrs=["10.0.0.0/24"])
        })

        print('Expose individual endpoints to different space/CIDR combinations')
        await application.expose(exposed_endpoints={
            "": ExposedEndpoint(to_spaces=["alpha"], to_cidrs=["10.0.0.0/24"]),
            "ubuntu": ExposedEndpoint(to_cidrs=["10.42.42.0/24"])
        })

        print('Unexpose individual endpoints (other endpoints remain exposed)')
        await application.unexpose(exposed_endpoints=["ubuntu"])

        print('Unexpose application')
        await application.unexpose()

        print('Removing ubuntu')
        await application.remove()
    finally:
        print('Disconnecting from model')
        await model.disconnect()


if __name__ == '__main__':
    loop.run(main())
