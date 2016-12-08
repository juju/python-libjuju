Creating and Destroying a Model
===============================
Example of creating a new model and then destroying it.

.. code:: python

  from juju.controller import Controller

  controller = Controller()
  await controller.connect_current()

  # Create our new model
  model = await controller.add_model(
      'mymodel',  # name of your new model
      'aws',      # name of the cloud to use
      'aws-tim',  # name of the credential to use
  )

  # Do stuff with our model...

  # Destroy the model
  await model.disconnect()
  await controller.destroy_model(model.info.uuid)
