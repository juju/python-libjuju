Controllers
===========
A Juju controller provides websocket endpoints for itself and each of its
models. In order to do anything useful, the juju lib must connect to one of
these endpoints.

Connecting to the controller endpoint is useful if you want to programmatically
create a new model. If the model you want to use already exists, you can
connect directly to it (see py:doc:`model`).

For API docs, see py:class:`juju.controller.Controller`.


Connecting to the Current Controller
------------------------------------
Connect to the currently active Juju controller (the one returned by
`juju switch`). This only works if you have the Juju CLI client installed.

.. code:: python

  from juju.controller import Controller

  controller = Controller()
  await controller.connect()


Connecting to a Named Controller
--------------------------------
Connect to a controller by name.

.. code:: python

  from juju.controller import Controller

  controller = Controller()
  await controller.connect('mycontroller')


Connecting with Authentication
------------------------------
You can control what user you are connecting with by specifying either a
username/password pair, or a macaroon or bakery client that can provide
a macaroon.


.. code:: python

  controller = Controller()
  await controller.connect(username='admin',
                           password='f53f08cfc32a2e257fe5393271d89d62')

  # or with a macaroon
  await controller.connect(macaroons=[
      {
          "Name": "macaroon-218d87053ad19626bcd5a0eef0bc9ba8bd4fbd80a968f52a5fd430b2aa8660df",
          "Value": "W3siY2F2ZWF0cyI6 ... jBkZiJ9XQ==",
          "Domain": "10.130.48.27",
          "Path": "/auth",
          "Secure": false,
          "HostOnly": true,
          "Expires": "2018-03-07T22:07:23Z",
      },
  ])

  # or with a bakery client
  from macaroonbakery.httpbakery import Client
  from http.cookiejar import FileCookieJar

  bakery_client=Client()
  bakery_client.cookies = FileCookieJar('cookies.txt')
  controller = Controller()
  await controller.connect(bakery_client=bakery_client)
  


Connecting with an Explicit Endpoint
------------------------------------
The most flexible, but also most verbose, way to connect is using the API
endpoint url and credentials directly. This method does NOT require the
Juju CLI client to be installed.

.. code:: python

  controller = Controller()
  await controller.connect(
      endpoint='10.0.4.171:17070',
      username='admin',
      password='f53f08cfc32a2e257fe5393271d89d62',
      cacert=None,  # Left out for brevity, but if you have a cert string you
                    # should pass it in. You can get the cert from the output
                    # of The `juju show-controller` command.
  )
