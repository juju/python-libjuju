import asyncio
import signal


def run(*steps):
    """
    Helper to run one or more async functions synchronously, with graceful
    handling of SIGINT / Ctrl-C.

    Returns the return value of the last function.
    """
    if not steps:
        return

    task = None
    run._sigint = False  # function attr to allow setting from closure
    loop = asyncio.get_event_loop()

    def abort():
        task.cancel()
        run._sigint = True

    loop.add_signal_handler(signal.SIGINT, abort)
    try:
        for step in steps:
            task = loop.create_task(step)
            loop.run_until_complete(asyncio.wait([task], loop=loop))
            if run._sigint:
                raise KeyboardInterrupt()
            if task.exception():
                raise task.exception()
        return task.result()
    finally:
        loop.remove_signal_handler(signal.SIGINT)
