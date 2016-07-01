# Front Matter

A python library for Juju.

NOTE: This is early work-in-progress, pre-alpha software. There is very little
implementation here yet. The design itself is not complete.  Comments on the
design, good or bad, are welcomed. Use cases are also appreciated as they will
shape the design.

The goal is to end up with a feature-full and officially supported python
library for Juju.

The focus right now is on Juju 2+ only.

# Design Notes

* Require python3.5+ (async/await) and juju-2.0+
* Auto-generate async (and sync? see below) websocket client from juju golang code
* Present an object-oriented interface to all the features of the Juju CLI
* Do as much as possible through the API so that the library can be used
	without actually installing Juju

# Implementation Status

There is an async websocket client that is auto-generated (indirectly) from the
juju golang code so that the entire api is supported. This is mostly working.
There will probably a synchronous client as well because why not.

On top of that will be an object-oriented layer that supports the full range of
operations that one could perform with the CLI (at least), which uses the
websocket client underneath but presents a friendlier interface. One advantage
of using an async client is that we can have a live-updating object layer,
where user code is informed of changes that are occurring to the underlying
juju model in real time. There is an example of what this might look like in
examples/livemodel.py.

# Example Use Cases

See the `examples/` directory for some simple working examples.

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
