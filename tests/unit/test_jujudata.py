# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import unittest

import mock
import pytest

from juju.client.jujudata import FileJujuData
from juju.errors import JujuControllerNotFoundError


class TestJujuData(unittest.IsolatedAsyncioTestCase):
    @mock.patch("io.open")
    async def test_verify_controller_uninitialized(self, mock_io_open):
        mock_io_open.side_effect = FileNotFoundError()
        jujudata = FileJujuData()
        with pytest.raises(JujuControllerNotFoundError):
            jujudata.current_controller()
