Models
======
A Juju controller provides websocket endpoints for each of its
models. In order to do anything useful with a model, the juju lib must
connect to one of these endpoints. There are several ways to do this.

For api docs, see :class:`juju.model.Model`.


Connecting to the Current Model
-------------------------------
Connect to the currently active Juju model (the one returned by
`juju switch`). This only works if you have the Juju CLI client installed.

.. code:: python

  from juju.model import Model

  model = Model()
  await model.connect_current()


Connecting to a Named Model
---------------------------
Connect to a model by name, using the same format as that returned from the
`juju switch` command. The accepted format is '[controller:][user/]model'.
This only works if you have the Juju CLI client installed.

.. code:: python

  # $ juju switch
  # juju-2.0.1:admin/libjuju

  from juju.model import Model

  model = Model()
  await model.connect_model('juju-2.0.1:admin/libjuju')


Connecting with Username/Password Authentication
------------------------------------------------
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


Connecting with Macaroon Authentication
---------------------------------------
To connect to a shared model, or a model an a shared controller, you'll need
to use macaroon authentication. The simplest example is shown below, and uses
already-discharged macaroons from the local filesystem. This will work if you
have the Juju CLI installed.

.. note::

  The library does not yet contain support for fetching and discharging
  macaroons. Until it does, if you want to use macaroon auth, you'll need
  to supply already-discharged macaroons yourself.

.. code:: python

  from juju.client.connection import get_macaroons()
  from juju.model import Model

  model = Model()

  controller_endpoint = '10.0.4.171:17070'
  model_uuid = 'e8399ac7-078c-4817-8e5e-32316d55b083'
  username = None
  password = None
  cacert = None
  macaroons = get_macaroons()

  await model.connect(
      controller_endpoint,
      model_uuid,
      username,
      password,
      cacert,
      macaroons,
  )


Creating and Destroying a Model
-------------------------------
Example of creating a new model and then destroying it. See
:meth:`juju.controller.Controller.add_model` and
:meth:`juju.controller.Controller.destroy_model` for more info.

.. code:: python

  from juju.controller import Controller

  controller = Controller()
  await controller.connect_current()

  # Create our new model
  model = await controller.add_model(
      'mymodel',  # name of your new model
  )

  # Do stuff with our model...

  # Destroy the model
  await model.disconnect()
  await controller.destroy_model(model.info.uuid)
  model = None
