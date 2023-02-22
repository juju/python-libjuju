import asynctest
import mock
import pytest

from juju.model import Model
from juju.machine import Machine


@asynctest.patch('juju.client.client.ClientFacade')
@pytest.mark.asyncio
async def test_hostname(mock_cf):
    model = Model()
    model._connector = mock.MagicMock()
    model.state = mock.MagicMock()

    # Calling hostname() when no information is available (e.g. targeting
    # an older controller, agent not started yet etc.) should return None
    model.state.entity_data = mock.MagicMock(return_value={})
    mach = Machine('test', model)
    assert mach.hostname is None

    model.state.entity_data = mock.MagicMock(return_value={
        'hostname': 'thundering-herds',
    })
    assert mach.hostname == 'thundering-herds'
