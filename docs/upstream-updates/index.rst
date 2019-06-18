Syncing Upstream Updates
========================

Updating the facade and definitions code generated from the schema
to reflect changes in upstream Juju consists of two steps:

* Creating a new `schemas-juju-<version>.json` file from the Juju code-base
* Generating the libjuju Python code from that schema

Additionally changes, although rare may be also required to add or
update an override.


Creating a Schema File
----------------------

Firstly, checkout the Juju_ project and correctly set it up according to
it's documentation. Juju_ has the ability to generate the schema and stores
it in version control (git). Copy that file from Juju_ to libjuju repository
to make sure it can be picked up for construction of the libjuju client.

From inside Juju_:

.. code:: bash

  make rebuild-schema

The version number used in the filename should match the upstream
version of Juju. To ensure that the client picks up the new change, the
`latest` pointer (schemas-juju-latest.json) should be pointed to the
versioned file:

From inside libjuju:

.. code:: bash

  cp ${GOPATH}/src/github.com/juju/juju/apiserver/facades/schema.json \
      juju/client/schemas-juju-2.6.4.json
  rm juju/client/schemas-juju-latest.json
  ln -s schemas-juju-2.6.4.json juju/client/schemas-juju-latest.json


Generating the Python Code
--------------------------

Creating a new client requires the building of the Python code from
the schema and doing so is a make target:

.. code:: bash

  make client

Changes to `juju/client/_definitions.py` and `juju/client/_clientX.py`
files are expected, along with any facades files, depending what was
changed in Juju_.


Integrating into the Object Layer
---------------------------------

Once the raw client APIs are synced, you may need to integrate any new or
changed API calls into the object layer, to provide a clean, Pythonic way
to interact with the model.  This may be as simple as adding an optional
parameter to an existing model method, tweaking what manipulations, if any
the model method does to the data before it is sent to the API, or it may
require adding an entirely new model method to capture the new functionality.

In general, the approach should be to make the interactions with the model
layer use the same patterns as when you use the CLI, just with Python idioms
and OO approaches.

When trying to determine what client calls need to be made and what data to
be sent for a given Juju CLI action, it is very useful to add
`--debug --logging-config TRACE` to any Juju CLI command to view the full
conversation between the CLI client and the API server.  For example:

```
[johnsca@murdoch:~] $ juju deploy --debug --logging-config TRACE ./builds/test
11:51:20 INFO  juju.cmd supercommand.go:56 running juju [2.3.5 gc go1.10]
11:51:20 DEBUG juju.cmd supercommand.go:57   args: []string{"/snap/juju/3884/bin/juju", "deploy", "--debug", "--logging-config", "TRACE", "./builds/test"}
11:51:20 INFO  juju.juju api.go:67 connecting to API addresses: [35.172.119.191:17070 172.31.94.16:17070 252.94.16.1:17070]
11:51:20 TRACE juju.api certpool.go:49 cert dir "/etc/juju/certs.d" does not exist
11:51:20 DEBUG juju.api apiclient.go:843 successfully dialed "wss://35.172.119.191:17070/model/a7317969-6dab-4ba4-844b-af3d661c228d/api"
11:51:20 INFO  juju.api apiclient.go:597 connection established to "wss://35.172.119.191:17070/model/a7317969-6dab-4ba4-844b-af3d661c228d/api"
...
11:51:20 INFO  juju.cmd.juju.application series_selector.go:71 with the configured model default series "xenial"
11:51:20 DEBUG httpbakery client.go:244 client do POST https://35.172.119.191:17070/model/a7317969-6dab-4ba4-844b-af3d661c228d/charms?revision=0&schema=local&series=xenial {
11:51:21 DEBUG httpbakery client.go:246 } -> error <nil>
11:51:21 INFO  cmd deploy.go:1096 Deploying charm "local:xenial/test-0".
11:51:21 TRACE juju.rpc.jsoncodec codec.go:225 -> {"request-id":3,"type":"Charms","version":2,"request":"CharmInfo","params":{"url":"local:xenial/test-0"}}
11:51:21 TRACE juju.rpc.jsoncodec codec.go:120 <- {"request-id":3,"response":{"revision":0,"url":"local:xenial/test-0","config":{"test":{"type":"string","default":""}},"meta":{"name":"test","summary":"test","description":"test","subordinate":false,"series":["xenial"],"resources":{"dummy":{"name":"dummy","type":"file","path":"dummy.snap","description":"dummy snap"}},"min-juju-version":"0.0.0"},"actions":{}}}
11:51:21 TRACE juju.rpc.jsoncodec codec.go:225 -> {"request-id":4,"type":"Charms","version":2,"request":"IsMetered","params":{"url":"local:xenial/test-0"}}
11:51:21 TRACE juju.rpc.jsoncodec codec.go:120 <- {"request-id":4,"response":{"metered":false}}
11:51:21 TRACE juju.rpc.jsoncodec codec.go:225 -> {"request-id":5,"type":"Resources","version":1,"request":"AddPendingResources","params":{"tag":"application-test","url":"local:xenial/test-0","channel":"","macaroon":null,"resources":[{"name":"dummy","type":"file","path":"dummy.snap","description":"dummy snap","origin":"store","revision":-1,"fingerprint":"","size":0}]}}
11:51:21 TRACE juju.rpc.jsoncodec codec.go:120 <- {"request-id":5,"response":{"pending-ids":["c0ffdd92-da23-4fb2-8d41-d82d58423447"]}}
11:51:21 TRACE juju.rpc.jsoncodec codec.go:225 -> {"request-id":6,"type":"Application","version":5,"request":"Deploy","params":{"applications":[{"application":"test","series":"xenial","charm-url":"local:xenial/test-0","channel":"","num-units":1,"config-yaml":"","constraints":{},"resources":{"dummy":"c0ffdd92-da23-4fb2-8d41-d82d58423447"}}]}}
11:51:21 TRACE juju.rpc.jsoncodec codec.go:120 <- {"request-id":6,"response":{"results":[{}]}}
11:51:21 TRACE juju.rpc.jsoncodec codec.go:123 <- error: read tcp 192.168.1.102:52168->35.172.119.191:17070: use of closed network connection (closing true)
11:51:21 DEBUG juju.api monitor.go:35 RPC connection died
11:51:21 INFO  cmd supercommand.go:465 command finished
```

Note that this will contain login information (which has been removed from the above).


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


.. _Juju: https://github.com/juju/juju
