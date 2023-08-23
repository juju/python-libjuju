# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import unittest

from juju import jasyncio


class TestLoop(unittest.TestCase):
    def setUp(self):
        # new event loop for each test
        policy = jasyncio.get_event_loop_policy()
        self.loop = policy.new_event_loop()
        policy.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    async def test_run(self):
        assert jasyncio.get_running_loop() == self.loop

        async def _test():
            return 'success'
        self.assertEqual(jasyncio.run(_test()), 'success')

    async def test_run_interrupt(self):
        async def _test():
            jasyncio.run._sigint = True
        self.assertRaises(KeyboardInterrupt, jasyncio.run, _test())

    async def test_run_exception(self):
        async def _test():
            raise ValueError()
        self.assertRaises(ValueError, jasyncio.run, _test())
