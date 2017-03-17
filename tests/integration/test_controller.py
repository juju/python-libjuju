import asyncio
from concurrent.futures import ThreadPoolExecutor
import pytest

from .. import base
from juju.controller import Controller

MB = 1
GB = 1024


@base.bootstrapped
@pytest.mark.asyncio
async def test_relate(event_loop):
    from juju.relation import Relation

    async with base.CleanModel() as model:
        await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='trusty',
            channel='stable',
        )
        await model.deploy(
            'nrpe',
            application_name='nrpe',
            series='trusty',
            channel='stable',
            # subordinates must be deployed without units
            num_units=0,
        )
        my_relation = await model.add_relation(
            'ubuntu',
            'nrpe',
        )

        assert isinstance(my_relation, Relation)


async def _deploy_in_loop(new_loop, model_name):
    new_model = Model(new_loop)
    await new_model.connect_model(model_name)
    try:
        await new_model.deploy('cs:xenial/ubuntu')
        assert 'ubuntu' in new_model.applications
    finally:
        await new_model.disconnect()
