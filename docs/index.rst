.. libjuju documentation master file, created by
   sphinx-quickstart on Thu May 19 11:21:38 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

A Python library for Juju
=========================

NOTE: This is pre-release software. The implementation is usable but
not complete.

Please report bugs at https://github.com/juju/python-libjuju/issues.


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

    git clone https://github.com/juju/python-libjuju.git
    cd python-libjuju
    python setup.py install  # make sure python is 3.5+


Quickstart
----------
Here's a simple example that shows basic usage of the library. The example
connects to the currently active Juju model, deploys a single unit of the
ubuntu charm, then exits.

More examples can be found in the `examples/` directory of the source tree,
and in the documentation.


.. code:: python

  #!/usr/bin/python3.5

  import asyncio
  import logging

  from juju.model import Model


  async def run():
      # Create a Model instance. We need to connect our Model to a Juju api
      # server before we can use it.
      model = Model()

      # Connect to the currently active Juju model
      await model.connect_current()

      # Deploy a single unit of the ubuntu charm, using revision 0 from the
      # stable channel of the Charm Store.
      ubuntu_app = await model.deploy(
          'ubuntu-0',
          service_name='ubuntu',
          series='xenial',
          channel='stable',
      )

      # Disconnect from the api server and cleanup.
      model.disconnect()

      # Stop the asyncio event loop.
      model.loop.stop()


  def main():
      # Set logging level to debug so we can see verbose output from the
      # juju library.
      logging.basicConfig(level=logging.DEBUG)

      # Quiet logging from the websocket library. If you want to see
      # everything sent over the wire, set this to DEBUG.
      ws_logger = logging.getLogger('websockets.protocol')
      ws_logger.setLevel(logging.INFO)

      # Create the asyncio event loop
      loop = asyncio.get_event_loop()

      # Queue up our `run()` coroutine for execution
      loop.create_task(run())

      # Start the event loop
      loop.run_forever()


  if __name__ == '__main__':
      main()


Table of Contents
-----------------

.. toctree::
   :glob:
   :maxdepth: 3

   narrative/index
   API Docs <api/modules>



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

