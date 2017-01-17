import unittest
import juju.loop


class TestLoop(unittest.TestCase):
    def test_run(self):
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
