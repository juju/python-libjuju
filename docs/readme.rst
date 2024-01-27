A Python library for Juju
=========================

Source code: https://github.com/juju/python-libjuju

Bug reports: https://github.com/juju/python-libjuju/issues

Documentation: https://pythonlibjuju.readthedocs.io/en/latest/


Requirements
------------

* Python 3.9/3.10


Design Notes
------------

* Asynchronous - Uses asyncio and async/await features of Python
* Websocket-level bindings are programmatically generated (indirectly) from the
  Juju golang code, ensuring full api coverage
* Provides an OO layer which encapsulates much of the websocket api and
  provides familiar nouns and verbs (e.g. Model.deploy(), Application.add_unit(),
  etc.)


Installation
------------

.. code:: bash

  pip3 install juju


Quickstart
----------

Here's a simple example that shows basic usage of the library. The example
connects to the currently active Juju model, deploys a single unit of the
ubuntu charm, then exits:

Note : Pylibjuju requires an already bootstrapped Juju controller to connect to.

.. code:: python

  #!/usr/bin/python3

  import logging
  import sys

  from juju import jasyncio
  from juju.model import Model


  async def deploy():
      # Create a Model instance. We need to connect our Model to a Juju api
      # server before we can use it.
      model = Model()

      # Connect to the currently active Juju model
      await model.connect()

      try:
          # Deploy a single unit of the ubuntu charm, using the latest revision
          # from the stable channel of the Charm Store.
          ubuntu_app = await model.deploy(
            'ubuntu',
            application_name='my-ubuntu',
          )

          if '--wait' in sys.argv:
              # optionally block until the application is ready
              await model.wait_for_idle(status = 'active')

      finally:
          # Disconnect from the api server and cleanup.
          await model.disconnect()


  def main():
      logging.basicConfig(level=logging.INFO)

      # If you want to see everything sent over the wire, set this to DEBUG.
      ws_logger = logging.getLogger('websockets.protocol')
      ws_logger.setLevel(logging.INFO)

      # Run the deploy coroutine in an asyncio event loop, using a helper
      # that abstracts loop creation and teardown.
      jasyncio.run(deploy())


  if __name__ == '__main__':
      main()


More examples can be found in the docs, as well as in the ``examples/``
directory of the source tree which can be run using ``tox``.  For
example, to run ``examples/connect_current_model.py``, use:

.. code:: bash

  tox -e example -- examples/connect_current_model.py


REPL
^^^^

To experiment with the library in a REPL, launch python in asyncio mode

.. code:: bash

  $ python3 -m asyncio

and then, to connect to the current model and fetch status:

.. code::

  >>> from juju.model import Model
  >>> model = Model()
  >>> await model.connect_current()
  >>> status = await model.get_status()


Versioning
----------

The current Pylibjuju release policy tracks the Juju release cadence.
In particular, whenever Juju makes a latest/stable release, pylibjuju pushes out
a release with the same version in the following week. Newly generated schemas
will be updated per Juju releases.
