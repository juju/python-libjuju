.. libjuju documentation master file, created by
   sphinx-quickstart on Thu May 19 11:21:38 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

A Python library for Juju
=========================

Front Matter
------------

NOTE: There is no implementation here yet. It is simply a mocked out
design of what this library might look like. The design itself is not
complete. Comments on the design, good or bad, are welcomed. Use cases
are also appreciated as they will shape the design.

The goal is to end up with a feature-full and officially supported
python library for Juju.

The focus right now is on Juju 2+ only.

Design Ideas
------------

* Present an object-oriented interface to all the features of the Juju
  CLI
* Do as much as possible through the API so that the library can be used
  without actually installing Juju

Example Use Cases
-----------------

Please add more!

Simple bootstrap/deploy
+++++++++++++++++++++++

.. code:: python

  from juju import Juju

  juju = Juju()
  lxd = juju.get_cloud('lxd')
  controller = lxd.bootstrap('lxd-test')
  model = controller.get_model('default')

  # We might want an async and blocking version of deploy()?
  model.deploy('mediawiki-single')

  mediawiki = model.get_service('mediawiki')
  mediawiki.expose()


Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   api/modules



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

