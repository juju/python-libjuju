Units
=====

Running Commands
----------------
Run arbitrary commands on a unit with the
:meth:`juju.unit.Unit.run` method. This method blocks
the current coroutine until a result is available, and
returns a :class:`juju.action.Action` instance.


.. code:: python

  from juju.model import Model

  model = Model()
  await model.connect_current()

  ubuntu_app = await model.deploy(
      'ubuntu',
      application_name='ubuntu',
      series='trusty',
      channel='stable',
  )

  for unit in app.units:
      action = await unit.run('unit-get public-address')
      print(action.results)

      action = await unit.run('uname -a')
      print(action.results)


