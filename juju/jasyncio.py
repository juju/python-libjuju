# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

# A compatibility layer on asyncio that ensures we have all the right
# bindings for the functions we need from asyncio. Reason for this
# layer is the frequent functional changes, additions and deprecations
# in asyncio across the different Python versions.

# Any module that needs to use the asyncio should get the binding from
# this layer.

import asyncio
import signal
import functools
import websockets
import logging

ROOT_LOGGER = logging.getLogger()

from asyncio import Event, TimeoutError, Queue, ensure_future, \
    gather, sleep, wait_for, create_subprocess_exec, subprocess, \
    wait, FIRST_COMPLETED, Lock, as_completed, new_event_loop, \
    get_event_loop_policy, CancelledError, get_running_loop, \
    create_task, ALL_COMPLETED, all_tasks, current_task, shield     # noqa


def create_task_with_handler(coro, task_name, logger=ROOT_LOGGER):
    """Wrapper around "asyncio.create_task" to make sure the task
    exceptions are handled properly.

    asyncio loop event_handler is only called on task exceptions when
    the Task object is cleared from memory. But the GC doesn't clear
    the Task if we keep a reference for it (e.g. _pinger_task in
    connection.py) until the very end.

    This makes sure the exceptions are retrieved and properly
    handled/logged whenever the Task is destroyed.
    """
    def _task_result_exp_handler(task, task_name=task_name, logger=logger):
        try:
            task.result()
        except CancelledError:
            pass
        except websockets.exceptions.ConnectionClosed:
            return
        except Exception as e:
            # This really is an arbitrary exception we need to catch
            #
            # No need to re-raise, though, because after this point
            # the only thing that can catch this is asyncio loop base
            # event_handler, which won't do anything but yell 'Task
            # exception was never retrieved' anyways.
            logger.exception("Task %s raised an exception: %s" % (task_name, e))

    task = create_task(coro)
    task.add_done_callback(functools.partial(_task_result_exp_handler, task_name=task_name, logger=logger))
    return task


class SingletonEventLoop(object):
    """
    Single instance containing an event loop to be reused.
    """

    loop = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonEventLoop, cls).__new__(cls)
            cls.instance.loop = asyncio.new_event_loop()

        return cls.instance


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
    # Use a singleton class to force a single event loop instance
    loop = SingletonEventLoop().loop

    def abort():
        task.cancel()
        run._sigint = True

    added = False
    try:
        loop.add_signal_handler(signal.SIGINT, abort)
        added = True
    except (ValueError, OSError, RuntimeError) as e:
        # add_signal_handler doesn't work in a thread
        if 'main thread' not in str(e):
            raise
    try:
        for step in steps:
            task = loop.create_task(step)
            loop.run_until_complete(wait([task]))
            if run._sigint:
                raise KeyboardInterrupt()
            if task.exception():
                raise task.exception()
        return task.result()
    finally:
        if added:
            loop.remove_signal_handler(signal.SIGINT)
