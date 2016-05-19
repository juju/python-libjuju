# Front Matter

A python library for Juju.

NOTE: There is no implementation here yet. It is simply a mocked out
design of what this library might look like. The design itself is not
complete. Comments on the design, good or bad, are welcomed. Use cases
are also appreciated as they will shape the design.

The goal is to end up with a feature-full and officially supported
python library for Juju.

The focus right now is on Juju 2+ only.

# Design Ideas

* Present an object-oriented interface to all the features of the Juju
  CLI
* Do as much as possible through the API so that the library can be used
  without actually installing Juju

# Example Use Cases

Please add more!

## Simple bootstrap/deploy

```python
from juju import Juju

juju = Juju()
lxd = juju.get_cloud('lxd')
controller = lxd.bootstrap('lxd-test')
model = controller.get_model('default')

# We might want an async and blocking version of deploy()?
model.deploy('mediawiki-single')

mediawiki = model.get_service('mediawiki')
mediawiki.expose()
```
