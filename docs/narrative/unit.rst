Units
=====
For api docs, see :class:`juju.unit.Unit`.


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

  app = await model.deploy(
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


Running Actions
---------------
Run actions on a unit with the
:meth:`juju.unit.Unit.run_action` method. This method
returns a :class:`juju.action.Action` instance immediately. To block until
the action completes, use the :meth:`juju.action.Action.wait` method, as
in the example below.


.. code:: python

  from juju.model import Model

  model = Model()
  await model.connect_current()

  app = await model.deploy(
      'git',
      application_name='git',
      series='trusty',
      channel='stable',
  )

  for unit in app.units:
      # run the 'add-repo' action, passing a 'repo' param
      action = await unit.run_action('add-repo', repo='myrepo')
      # wait for the action to complete
      action = await action.wait()

      print(action.results)
