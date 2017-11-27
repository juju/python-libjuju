import asyncio
import unittest

import juju.loop


class TestLoop(unittest.TestCase):
    def setUp(self):
        # new event loop for each test
        policy = asyncio.get_event_loop_policy()
        self.loop = policy.new_event_loop()
        policy.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_run(self):
        assert asyncio.get_event_loop() == self.loop

        async def _test():
            return 'success'
        self.assertEqual(juju.loop.run(_test()), 'success')

    def test_run_interrupt(self):
        async def _test():
            juju.loop.run._sigint = True
        self.assertRaises(KeyboardInterrupt, juju.loop.run, _test())

    def test_run_exception(self):
        async def _test():
            raise ValueError()
        self.assertRaises(ValueError, juju.loop.run, _test())
