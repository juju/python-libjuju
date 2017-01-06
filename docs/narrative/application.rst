Applications
============
For api docs, see :class:`juju.application.Application`.


Deploying
---------
To deploy a new application, connect a model and then call its
:meth:`~juju.model.Model.deploy` method. An
:class:`~juju.application.Application` instance is returned.

.. code:: python

  from juju.model import Model

  model = Model()
  await model.connect_current()

  mysql_app = await model.deploy(
      # If a revision number is not included in the charm url,
      # the latest revision from the Charm Store will be used.
      'cs:mysql-55',
      application_name='mysql',
      series='trusty',
      channel='stable',
      config={
          'tuning-level': 'safest',
      },
      constraints={
          'mem': 256 * MB,
      },
  )


Deploying a Local Charm
-----------------------
To deploy a local charm, pass the charm directory path to
`Model.deploy()`.

.. code:: python

  from juju.model import Model

  model = Model()
  await model.connect_current()

  # Deploy a local charm using a path to the charm directory
  await model.deploy(
      '/home/tvansteenburgh/src/charms/ubuntu',
      application_name='ubuntu',
      series='trusty',
  )


Adding Units
------------
To add units to a deployed application, use the
:meth:`juju.application.Application.add_units` method. A list of the newly
added units (:class:`~juju.unit.Unit` objects) is returned.

.. code:: python

  ubuntu_app = await model.deploy(
      'ubuntu',
      application_name='ubuntu',
      series='trusty',
      channel='stable',
  )

  unit_a, unit_b = await ubuntu_app.add_units(count=2)


Updating Config and Constraints
-------------------------------
Example showing how to update configuration and constraints on a deployed
application. The `mysql_app` object is an instance of
:class:`juju.application.Application`.

.. code:: python

  MB = 1024 * 1024

  # Update and check app config
  await mysql_app.set_config({'tuning-level': 'fast'})
  config = await mysql_app.get_config()

  assert(config['tuning-level']['value'] == 'fast')

  # update and check app constraints
  await mysql_app.set_constraints({'mem': 512 * MB})
  constraints = await mysql_app.get_constraints()

  assert(constraints['mem'] == 512 * MB)


Adding and Removing Relations
-----------------------------
The :meth:`juju.application.Application.add_relation` method returns a
:class:`juju.relation.Relation` instance.

.. code:: python

  from juju.model import Model

  model = Model()
  await model.connect_current()

  # Deploy mysql-master application
  mysql_master = await model.deploy(
      'cs:mysql-55',
      application_name='mysql-master',
      series='trusty',
      channel='stable',
  )

  # Deploy mysql-slave application
  mysql_slave = await model.deploy(
      'cs:mysql-55',
      application_name='mysql-slave',
      series='trusty',
      channel='stable',
  )

  # Add the master-slave relation
  relation = await mysql_master.add_relation(
      # Name of the relation on the local (mysql-master) side
      'master',
      # Name of the app:relation on the remote side
      'mysql-slave:slave',
  )

  # Remove the relation
  await mysql_master.remove_relation(
      'master',
      'mysql-slave:slave',
  )
