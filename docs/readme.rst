A Python library for Juju
=========================

Source code: https://github.com/juju/python-libjuju

Bug reports: https://github.com/juju/python-libjuju/issues

Documentation: https://pythonlibjuju.readthedocs.io/en/latest/


Requirements
------------

* Python 3.5+
* Juju 2.0+


Design Notes
------------

* Asynchronous - uses asyncio and async/await features of python 3.5
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


.. code:: python

  #!/usr/bin/python3

  import logging
  import sys

  from juju import loop
  from juju.model import Model


  async def deploy():
      # Create a Model instance. We need to connect our Model to a Juju api
      # server before we can use it.
      model = Model()

      # Connect to the currently active Juju model
      await model.connect_current()

      try:
          # Deploy a single unit of the ubuntu charm, using the latest revision
          # from the stable channel of the Charm Store.
          ubuntu_app = await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='xenial',
            channel='stable',
          )

          if '--wait' in sys.argv:
              # optionally block until the application is ready
              await model.block_until(lambda: ubuntu_app.status == 'active')
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
      loop.run(deploy())


  if __name__ == '__main__':
      main()


More examples can be found in the docs, as well as in the ``examples/``
directory of the source tree which can be run using ``tox``.  For
example, to run ``examples/connect_current_model.py``, use:

.. code:: bash

  tox -e example -- examples/connect_current_model.py


Versioning
----------

Pylibjuju releases now track the Juju release cadence. New generated schemas
will be updated per Juju releases.
