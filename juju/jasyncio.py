# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

# A compatibility layer on asyncio that ensures we have all the right
# bindings for the functions we need from asyncio. Reason for this
# layer is the frequent functional changes, additions and deprecations
# in asyncio across the different Python versions.

# Any module that needs to use the asyncio should get the binding from
# this layer.

import asyncio
import functools
import logging
import signal
from asyncio import (
    ALL_COMPLETED as ALL_COMPLETED,
)
from asyncio import (
    FIRST_COMPLETED as FIRST_COMPLETED,
)
from asyncio import (
    CancelledError,
    Task,
    create_task,
    wait,
)

# FIXME: integration tests don't use these, but some are used in this repo
# Use primitives from asyncio within this repo and remove these re-exports
from asyncio import (
    Event as Event,
)
from asyncio import (
    Lock as Lock,
)
from asyncio import (
    Queue as Queue,
)
from asyncio import (
    TimeoutError as TimeoutError,  # noqa: A004
)
from asyncio import (
    all_tasks as all_tasks,
)
from asyncio import (
    as_completed as as_completed,
)
from asyncio import (
    create_subprocess_exec as create_subprocess_exec,
)
from asyncio import (
    current_task as current_task,
)
from asyncio import (
    ensure_future as ensure_future,
)
from asyncio import (
    gather as gather,
)
from asyncio import (
    get_event_loop_policy as get_event_loop_policy,
)
from asyncio import (
    get_running_loop as get_running_loop,
)
from asyncio import (
    new_event_loop as new_event_loop,
)
from asyncio import (
    shield as shield,
)
from asyncio import (
    sleep as sleep,
)
from asyncio import (
    subprocess as subprocess,
)
from asyncio import (
    wait_for as wait_for,
)

import websockets

ROOT_LOGGER = logging.getLogger()


def create_task_with_handler(coro, task_name, logger=ROOT_LOGGER) -> Task:
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
    task.add_done_callback(
        functools.partial(_task_result_exp_handler, task_name=task_name, logger=logger)
    )
    return task


class SingletonEventLoop:
    """Single instance containing an event loop to be reused."""

    loop = None

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
            cls.instance.loop = asyncio.new_event_loop()

        return cls.instance


def run(*steps):
    """Helper to run one or more async functions synchronously, with graceful
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
        if "main thread" not in str(e):
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
