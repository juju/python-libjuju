Creating and Destroying a Model
===============================
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
