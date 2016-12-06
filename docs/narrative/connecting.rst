Connecting
==========
A Juju controller provides websocket endpoints for itself and each of its
models. In order to do anything useful, the juju lib must connect to one of
these endpoints. There are several ways to do this.


To the Current Model
--------------------
Connect to the currently active Juju model (the one returned by
`juju switch`). This only works if you have the Juju CLI client installed.

.. code:: python

  from juju.model import Model

  model = Model()
  await model.connect_current()


To a Named Model
----------------
Connect to a model by name, using the same format as that returned from the
`juju switch` command. The accepted format is '[controller:][user/]model'.
This only works if you have the Juju CLI client installed.

.. code:: python

  # $ juju switch
  # juju-2.0.1:admin/libjuju

  from juju.model import Model

  model = Model()
  await model.connect_model('juju-2.0.1:admin/libjuju')


To an API Endpoint with Username/Password Authentication
--------------------------------------------------------
The most flexible, but also most verbose, way to connect is using the API
endpoint url and credentials directly. This method does NOT require the Juju
CLI client to be installed.

.. code:: python

  from juju.model import Model

  model = Model()

  controller_endpoint = '10.0.4.171:17070'
  model_uuid = 'e8399ac7-078c-4817-8e5e-32316d55b083'
  username = 'admin'
  password = 'f53f08cfc32a2e257fe5393271d89d62'

  # Left out for brevity, but if you have a cert string you should pass it in.
  # You can copy the cert from the output of The `juju show-controller`
  # command.
  cacert = None

  await model.connect(
      controller_endpoint,
      model_uuid,
      username,
      password,
      cacert,
  )
