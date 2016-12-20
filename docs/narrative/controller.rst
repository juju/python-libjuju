Controllers
===========
A Juju controller provides websocket endpoints for itself and each of its
models. In order to do anything useful, the juju lib must connect to one of
these endpoints.

Connecting to the controller endpoint is useful if you want to programmatically
create a new model. If the model you want to use already exists, you can
connect directly to it (see :doc:`model`).

For api docs, see :class:`juju.controller.Controller`.


Connecting to the Current Controller
------------------------------------
Connect to the currently active Juju controller (the one returned by
`juju switch`). This only works if you have the Juju CLI client installed.

.. code:: python

  from juju.controller import Controller

  controller = Controller()
  await controller.connect_current()


Connecting to a Named Controller
--------------------------------
Connect to a controller by name.

.. code:: python

  from juju.controller import Controller

  controller = Controller()
  await controller.connect_controller('mycontroller')


Connecting with Username/Password Authentication
------------------------------------------------
The most flexible, but also most verbose, way to connect is using the API
endpoint url and credentials directly. This method does NOT require the Juju
CLI client to be installed.

.. code:: python

  from juju.controller import Controller

  controller = Controller()

  controller_endpoint = '10.0.4.171:17070'
  username = 'admin'
  password = 'f53f08cfc32a2e257fe5393271d89d62'

  # Left out for brevity, but if you have a cert string you should pass it in.
  # You can copy the cert from the output of The `juju show-controller`
  # command.
  cacert = None

  await controller.connect(
      controller_endpoint,
      username,
      password,
      cacert,
  )


Connecting with Macaroon Authentication
---------------------------------------
To connect to a shared controller, you'll need
to use macaroon authentication. The simplest example is shown below, and uses
already-discharged macaroons from the local filesystem. This will work if you
have the Juju CLI installed.

.. note::

  The library does not yet contain support for fetching and discharging
  macaroons. Until it does, if you want to use macaroon auth, you'll need
  to supply already-discharged macaroons yourself.

.. code:: python

  from juju.client.connection import get_macaroons()
  from juju.controller import Controller

  controller = Controller()

  controller_endpoint = '10.0.4.171:17070'
  username = None
  password = None
  cacert = None
  macaroons = get_macaroons()

  await controller.connect(
      controller_endpoint,
      username,
      password,
      cacert,
      macaroons,
  )
