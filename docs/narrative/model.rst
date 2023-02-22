Models
======
A Juju controller provides websocket endpoints for each of its
models. In order to do anything useful with a model, the juju lib must
connect to one of these endpoints. There are several ways to do this.

For api docs, see py:class:`juju.model.Model`.


Connecting to the Current Model
-------------------------------
Connect to the currently active Juju model (the one returned by
`juju switch`). This only works if you have the Juju CLI client installed.

.. code:: python

  model = Model()
  await model.connect()


Connecting to a Named Model
---------------------------
Connect to a model by name, using the same format as that returned from the
`juju switch` command. The accepted format is '[controller:][user/]model'.
This only works if you have the Juju CLI client installed.

.. code:: python

  model = Model()
  await model.connect('juju-2.0.1:admin/libjuju')


Connecting with Authentication
------------------------------
You can control what user you are connecting with by specifying either a
username/password pair, or a macaroon or bakery client that can provide
a macaroon.


.. code:: python

  model = Model()
  await model.connect(username='admin',
                      password='f53f08cfc32a2e257fe5393271d89d62')

  # or with a macaroon
  await model.connect(macaroons=[
      {
          "Name": "macaroon-218d87053ad19626bcd5a0eef0bc9ba8bd4fbd80a968f52a5fd430b2aa8660df",
          "Value": "W3siY2F2ZWF0cyI6 ... jBkZiJ9XQ==",
          "Domain": "10.130.48.27",
          "Path": "/auth",
          "Secure": false,
          "HostOnly": true,
          "Expires": "2018-03-07T22:07:23Z",
      },
  ])

  # or with a bakery client
  from macaroonbakery.httpbakery import Client
  from http.cookiejar import FileCookieJar

  bakery_client=Client()
  bakery_client.cookies = FileCookieJar('cookies.txt')
  model = Model()
  await model.connect(bakery_client=bakery_client)
  


Connecting with an Explicit Endpoint
------------------------------------
The most flexible, but also most verbose, way to connect is using the API
endpoint url, model UUID, and credentials directly. This method does NOT
require the Juju CLI client to be installed.

.. code:: python

  from juju.model import Model

  model = Model()
  await model.connect(
      endpoint='10.0.4.171:17070',
      uuid='e8399ac7-078c-4817-8e5e-32316d55b083',
      username='admin',
      password='f53f08cfc32a2e257fe5393271d89d62',
      cacert=None,  # Left out for brevity, but if you have a cert string you
                    # should pass it in. You can get the cert from the output
                    # of The `juju show-controller` command.
  )


Creating and Destroying a Model
-------------------------------
Example of creating a new model and then destroying it. See
py:method:`juju.controller.Controller.add_model` and
py:method:`juju.controller.Controller.destroy_model` for more info.

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
  model_uuid = model.info.uuid
  await model.disconnect()
  await controller.destroy_model(model_uuid)
  model = None


Adding Machines and Containers
------------------------------
To add a machine or container, connect to a model and then call its
py:method:`~juju.model.Model.add_machine` method. A
py:class:`~juju.machine.Machine` instance is returned. The machine id
can be used to deploy a charm to a specific machine or container.

.. code:: python

  from juju.model import Model

  MB = 1
  GB = 1024


  model = Model()
  await model.connect_current()

  # add a new default machine
  machine1 = await model.add_machine()

  # add a machine with constraints, disks, and series specified
  machine2 = await model.add_machine(
      constraints={
          'mem': 256 * MB,
      },
      disks=[{
          'pool': 'rootfs',
          'size': 10 * GB,
          'count': 1,
      }],
      series='xenial',
  )

  # add a lxd container to machine2
  machine3 = await model.add_machine(
      'lxd:{}'.format(machine2.id))

  # deploy charm to the lxd container
  application = await model.deploy(
      'ubuntu-10',
      application_name='ubuntu',
      series='xenial',
      channel='stable',
      to=machine3.id
  )

  # remove application
  await application.remove()

  # destroy machines - note that machine3 must be destroyed before machine2
  # since it's a container on machine2
  await machine3.destroy(force=True)
  await machine2.destroy(force=True)
  await machine1.destroy(force=True)


Reacting to Changes in a Model
------------------------------
To watch for and respond to changes in a model, register an observer with the
model. The easiest way to do this is by creating a
py:class:`juju.model.ModelObserver` subclass.

.. code:: python

  from juju.model import Model, ModelObserver

  class MyModelObserver(ModelObserver):
      async def on_change(self, delta, old, new, model):
          # The raw change data (dict) from the websocket.
          print(delta.data)

          # The entity type (str) affected by this change.
          # One of ('action', 'application', 'annotation', 'machine',
          # 'unit', 'relation')
          print(delta.entity)

          # The type (str) of change.
          # One of ('add', 'change', 'remove')
          print(delta.type)

          # The 'old' and 'new' parameters are juju.model.ModelEntity
          # instances which represent an entity in the model both before
          # this change was applied (old) and after (new).

          # If an entity is being added to the model, the 'old' param
          # will be None.
          if delta.type == 'add':
              assert(old is None)

          # If an entity is being removed from the model, the 'new' param
          # will be None.
          if delta.type == 'remove':
              assert(new is None)

          # The 'old' and 'new' parameters, when not None, will be instances
          # of a juju.model.ModelEntity subclass. The type of the subclass
          # depends on the value of 'delta.entity', for example:
          #
          # delta.entity     type
          # ------------     ----
          # 'action'      -> juju.action.Action
          # 'application' -> juju.application.Application
          # 'annotation'  -> juju.annotation.Annotation
          # 'machine'     -> juju.machine.Machine
          # 'unit'        -> juju.unit.Unit
          # 'relation'    -> juju.relation.Relation

          # Finally, the 'model' parameter is a reference to the
          # juju.model.Model instance to which this observer is attached.
          print(id(model))


  model = Model()
  await model.connect_current()

  model.add_observer(MyModelObserver())


Every change in the model will result in a call to the `on_change()`
method of your observer(s).

To target your code more precisely, define method names that correspond
to the entity and type of change that you wish to handle.

.. code:: python

  from juju.model import Model, ModelObserver

  class MyModelObserver(ModelObserver):
      async def on_application_change(self, delta, old, new, model):
          # Both 'old' and 'new' params will be instances of
          # juju.application.Application
          pass

      async def on_unit_remove(self, delta, old, new, model):
          # Since a unit is being removed, the 'new' param will always
          # be None in this handler. The 'old' param will be an instance
          # of juju.unit.Unit - the state of the unit before it was removed.
          pass

      async def on_machine_add(self, delta, old, new, model):
          # Since a machine is being added, the 'old' param will always be
          # None in this handler. The 'new' param will be an instance of
          # juju.machine.Machine.
          pass

      async def on_change(self, delta, old, new, model):
          # The catch-all handler - will be called whenever a more
          # specific handler method is not defined.


Any py:class:`juju.model.ModelEntity` object can be observed directly by
registering callbacks on the object itself.

.. code:: python

  import logging

  async def on_app_change(delta, old, new, model):
      logging.debug('App changed: %r', new)

  async def on_app_remove(delta, old, new, model):
      logging.debug('App removed: %r', old)

  ubuntu_app = await model.deploy(
      'ubuntu',
      application_name='ubuntu',
      series='trusty',
      channel='stable',
  )
  ubuntu_app.on_change(on_app_change)
  ubuntu_app.on_remove(on_app_remove)
