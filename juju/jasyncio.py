# Copyright 2016 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

# A compatibility layer on asyncio that ensures we have all the right
# bindings for the functions we need from asyncio. Reason for this
# layer is the frequent functional changes, additions and deprecations
# in asyncio across the different Python versions.

# Any module that needs to use the asyncio should get the binding from
# this layer.

import signal

from asyncio import Event, TimeoutError, Queue, ensure_future, \
    gather, sleep, wait_for, create_subprocess_exec, subprocess, \
    wait, FIRST_COMPLETED, Lock, as_completed, get_event_loop_policy # noqa

try:
    from asyncio import get_running_loop
except ImportError:
    from asyncio import get_event_loop

    def get_running_loop():
        loop = get_event_loop()
        if not loop.is_running():
            raise RuntimeError("no running event loop")
        return loop


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
    loop = get_running_loop()

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
