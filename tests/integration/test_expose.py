# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import pytest

from juju.application import ExposedEndpoint

from .. import base


@base.bootstrapped
@pytest.mark.skip('Update charm')
async def test_expose_unexpose(event_loop):
    async with base.CleanModel() as model:
        app = await model.deploy(
            "ubuntu",
        )

        if not app.supports_granular_expose_parameters():
            pytest.skip("this test requires a 2.9 or greated controller")

        # Expose all opened port ranges
        await app.expose()
        exposed_endpoints = await get_exposed_endpoints(model, app)
        assert exposed_endpoints == {
            "": {
                "expose-to-cidrs": ["0.0.0.0/0", "::/0"],
                "expose-to-spaces": None
            }
        }

        # Expose all opened port ranges to the CIDRs that correspond to a list
        # of spaces.
        await app.expose(exposed_endpoints={
            "": ExposedEndpoint(to_spaces=["alpha"])
        })
        exposed_endpoints = await get_exposed_endpoints(model, app)
        assert exposed_endpoints == {
            "": {
                "expose-to-cidrs": None,
                "expose-to-spaces": ["alpha"]
            }
        }

        # Expose all opened port ranges to a list of CIDRs.
        await app.expose(exposed_endpoints={
            "": ExposedEndpoint(to_cidrs=["10.0.0.0/24"])
        })
        exposed_endpoints = await get_exposed_endpoints(model, app)
        assert exposed_endpoints == {
            "": {
                "expose-to-cidrs": ["10.0.0.0/24"],
                "expose-to-spaces": None
            }
        }

        # Expose all opened port ranges to a list of spaces and CIDRs.
        await app.expose(exposed_endpoints={
            "": ExposedEndpoint(to_spaces=["alpha"], to_cidrs=["10.0.0.0/24"])
        })
        exposed_endpoints = await get_exposed_endpoints(model, app)
        assert exposed_endpoints == {
            "": {
                "expose-to-spaces": ["alpha"],
                "expose-to-cidrs": ["10.0.0.0/24"]
            }
        }

        # Expose individual endpoints to different space/CIDR combinations
        await app.expose(exposed_endpoints={
            "": ExposedEndpoint(to_spaces=["alpha"], to_cidrs=["10.0.0.0/24"]),
            "ubuntu": ExposedEndpoint(to_cidrs=["10.42.42.0/24"])
        })
        exposed_endpoints = await get_exposed_endpoints(model, app)
        assert exposed_endpoints == {
            "": {
                "expose-to-spaces": ["alpha"],
                "expose-to-cidrs": ["10.0.0.0/24"]
            },
            "ubuntu": {
                "expose-to-cidrs": ["10.42.42.0/24"],
                "expose-to-spaces": None
            }
        }

        # Unexpose individual endpoints (other endpoints remain exposed).
        await app.unexpose(exposed_endpoints=["ubuntu"])
        exposed_endpoints = await get_exposed_endpoints(model, app)
        assert exposed_endpoints == {
            "": {
                "expose-to-spaces": ["alpha"],
                "expose-to-cidrs": ["10.0.0.0/24"]
            },
        }

        # Unexpose application
        await app.unexpose()
        exposed_endpoints = await get_exposed_endpoints(model, app)
        assert exposed_endpoints == {}


async def get_exposed_endpoints(model, app):
    app_name = app.name
    status = await model.get_status(filters=[app_name])
    exposed_endpoints = status.applications[app_name].exposed_endpoints
    return {k: v.serialize() for k, v in exposed_endpoints.items()}
