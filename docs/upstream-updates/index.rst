Upstream Updates
================

Updating the facade and definitions code generated from the schema
to reflect changes in upstream Juju consists of two steps:

* Creating a new `schemas-juju-<version>.json` file from the Juju code-base
* Generating the libjuju Python code from that schema

Rarely, you may also have to add or update an override.


Creating a Schema File
----------------------

First, you will need to fetch SchemaGen_ and a copy of the Juju source.
Once your copy of the Juju source is at the version you want to update to
(probably the `develop` branch, or a release tag) and you have updated
and reinstalled SchemaGen to reflect those changes, you just need to send
the output into a file in the libjuju repository:

.. code:: bash

  schemagen > juju/client/schemas-juju-2.2-rc1.json

The version number you use in the filename should match the upstream
version of Juju.  You should then also move the `latest` pointer to
the new file:

.. code:: bash

  rm juju/client/schemas-juju-latest.json
  ln -s schemas-juju-2.2-rc1.json juju/client/schemas-juju-latest.json


Generating the Python Code
--------------------------

Once you have a new schema file, you can update the Python code
using the `client` make target:

.. code:: bash

  make client

You should expect to see updates to the `juju/client/_definitions.py` file,
as well as one or more of the `juju/client/_clientX.py` files, depending on
which facades were touched.


Overrides
---------

It should be quite rare, but occasionally the generated Python code does
not capture all of the logic needed to properly parse the output from the API
or may otherwise need some small amount of tweaking.  This is what the
`juju/client/overrides.py` file is for.  An example of this is the `Number`
type, which isn't standard JSON and must be parsed slightly differently.

At the top of that file are two lists, `__all__` and `__patches__`.  The
former replaces entire class implementations, while the latter patches
the attributes of the override classes into the matching generated class,
leaving the rest of the generated class untouched.


.. _SchemaGen: https://github.com/juju/schemagen
