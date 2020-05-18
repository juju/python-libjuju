import pytest

from .. import base

MB = 1
GB = 1024


@base.bootstrapped
@pytest.mark.asyncio
async def test_juju_api_error(event_loop):
    '''
    Verify that we raise a JujuAPIError for responses with an error in
    a top level key (for completely invalid requests).

    '''
    from juju.errors import JujuAPIError

    async with base.CleanModel() as model:
        with pytest.raises(JujuAPIError):
            await model.add_machine(constraints={'mem': -50})


@base.bootstrapped
@pytest.mark.asyncio
async def test_juju_error_in_results_list(event_loop):
    '''
    Replicate the code that caused
    https://github.com/juju/python-libjuju/issues/67, and verify that
    we get a JujuError instead of passing silently by the failure.

    (We don't raise a JujuAPIError, because the request isn't
    completely invalid -- it's just passing a tag that doesn't exist.)

    This also verifies that we will raise a JujuError any time there
    is an error in one of a list of results.

    '''
    from juju.errors import JujuError
    from juju.client import client

    async with base.CleanModel() as model:
        ann_facade = client.AnnotationsFacade.from_connection(model.connection())

        ann = client.EntityAnnotations(
            entity='badtag',
            annotations={'gui-x': '1', 'gui-y': '1'},
        )
        with pytest.raises(JujuError):
            return await ann_facade.Set([ann])


@base.bootstrapped
@pytest.mark.asyncio
async def test_juju_error_in_result(event_loop):
    '''
    Verify that we raise a JujuError when appropraite when we are
    looking at a single result coming back.

    '''
    from juju.errors import JujuError
    from juju.client import client

    async with base.CleanModel() as model:
        app_facade = client.ApplicationFacade.from_connection(model.connection())

        with pytest.raises(JujuError):
            return await app_facade.GetCharmURL(application='foo')
