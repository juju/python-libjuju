# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import http
import logging
import socket
import ssl
from contextlib import closing
from pathlib import Path

from juju.client import client
from juju.client.connection import Connection
from juju.client.jujudata import FileJujuData
from juju.controller import Controller
from juju.utils import run_with_interrupt
from juju import jasyncio

import pytest
import websockets

from .. import base


logger = logging.getLogger(__name__)


@base.bootstrapped
async def test_monitor(event_loop):
    async with base.CleanModel() as model:
        conn = model.connection()
        assert conn.monitor.status == 'connected'
        await conn.close()

        assert conn.monitor.status == 'disconnecting'


@base.bootstrapped
async def test_monitor_catches_error(event_loop):

    async with base.CleanModel() as model:
        conn = model.connection()

        assert conn.monitor.status == 'connected'
        try:
            # grab the reconnect lock to prevent automatic
            # reconnecting during the test
            async with conn.monitor.reconnecting:
                await conn._ws.close()  # this could be racy with reconnect
                # if auto-reconnect is not disabled by lock, force this
                # test to fail by deferring to the reconnect task via sleep
                await jasyncio.sleep(0.1)
                assert conn.monitor.status == 'error'
        finally:
            await conn.close()


@base.bootstrapped
@pytest.mark.skip('Update charm')
async def test_full_status(event_loop):
    async with base.CleanModel() as model:
        await model.deploy(
            'ubuntu',
            application_name='ubuntu',
            series='focal',
            channel='stable',
        )

        c = client.ClientFacade.from_connection(model.connection())

        await c.FullStatus(patterns=None)


@base.bootstrapped
async def test_reconnect(event_loop):
    async with base.CleanModel() as model:
        kwargs = model.connection().connect_params()
        conn = await Connection.connect(**kwargs)
        try:
            await jasyncio.sleep(0.1)
            assert conn.is_open
            await conn._ws.close()
            assert not conn.is_open
            await model.block_until(lambda: conn.is_open, timeout=3)
        finally:
            await conn.close()


@base.bootstrapped
@pytest.mark.skip('tests the websocket protocol, not pylibjuju, needs to be revised')
async def test_redirect(event_loop):
    controller = Controller()
    await controller.connect()
    kwargs = controller.connection().connect_params()
    await controller.disconnect()

    # websockets.server.logger.setLevel(logging.DEBUG)
    # websockets.client.logger.setLevel(logging.DEBUG)
    # # websockets.protocol.logger.setLevel(logging.DEBUG)
    # logger.setLevel(logging.DEBUG)

    destination = 'wss://{}/api'.format(kwargs['endpoint'])
    redirect_statuses = [
        http.HTTPStatus.MOVED_PERMANENTLY,  # 301
        http.HTTPStatus.FOUND,
        http.HTTPStatus.SEE_OTHER,
        http.HTTPStatus.TEMPORARY_REDIRECT,
        http.HTTPStatus.PERMANENT_REDIRECT,
    ]
    test_server_cert = Path(__file__).with_name('cert.pem')
    kwargs['cacert'] += '\n' + test_server_cert.read_text()
    server = RedirectServer(destination)
    try:
        for status in redirect_statuses:
            logger.debug('test: starting {}'.format(status))
            server.start(status)
            await run_with_interrupt(server.running.wait(),
                                     server.terminated)
            if server.exception:
                raise server.exception
            assert not server.terminated.is_set()
            logger.debug('test: started')
            kwargs_copy = dict(kwargs,
                               endpoint='localhost:{}'.format(server.port))
            logger.debug('test: connecting')
            conn = await Connection.connect(**kwargs_copy)
            logger.debug('test: connected')
            await conn.close()
            logger.debug('test: stopping')
            server.stop()
            await server.stopped.wait()
            logger.debug('test: stopped')
    finally:
        server.terminate()
        await server.terminated.wait()


class RedirectServer:
    def __init__(self, destination):
        self.destination = destination
        self._start = jasyncio.Event()
        self._stop = jasyncio.Event()
        self._terminate = jasyncio.Event()
        self.running = jasyncio.Event()
        self.stopped = jasyncio.Event()
        self.terminated = jasyncio.Event()
        if hasattr(ssl, 'PROTOCOL_TLS_SERVER'):
            # python 3.6+
            protocol = ssl.PROTOCOL_TLS_SERVER
        self.ssl_context = ssl.SSLContext(protocol)
        crt_file = Path(__file__).with_name('cert.pem')
        key_file = Path(__file__).with_name('key.pem')
        self.ssl_context.load_cert_chain(str(crt_file), str(key_file))
        self.status = None
        self.port = None
        self._task = jasyncio.create_task(self.run())

    def start(self, status):
        self.status = status
        self.port = self._find_free_port()
        self._start.set()

    def stop(self):
        self._stop.set()

    def terminate(self):
        self._terminate.set()
        self.stop()

    @property
    def exception(self):
        try:
            return self._task.exception()
        except (jasyncio.CancelledError, jasyncio.InvalidStateError):
            return None

    async def run(self):
        logger.debug('server: active')

        async def hello(websocket, path):
            await websocket.send('hello')

        async def redirect(path, request_headers):
            return self.status, {'Location': self.destination}, b""

        try:
            while not self._terminate.is_set():
                await run_with_interrupt(self._start.wait(),
                                         self._terminate)
                if self._terminate.is_set():
                    break
                self._start.clear()
                logger.debug('server: starting {}'.format(self.status))
                try:
                    async with websockets.serve(ws_handler=hello,
                                                process_request=redirect,
                                                host='localhost',
                                                port=self.port,
                                                ssl=self.ssl_context,
                                                loop=jasyncio.get_running_loop()):
                        self.stopped.clear()
                        self.running.set()
                        logger.debug('server: started')
                        while not self._stop.is_set():
                            await run_with_interrupt(
                                jasyncio.sleep(1),
                                self._stop)
                            logger.debug('server: tick')
                        logger.debug('server: stopping')
                except jasyncio.CancelledError:
                    break
                finally:
                    self.stopped.set()
                    self._stop.clear()
                    self.running.clear()
                    logger.debug('server: stopped')
            logger.debug('server: terminating')
        except jasyncio.CancelledError:
            pass
        finally:
            self._start.clear()
            self._stop.clear()
            self._terminate.clear()
            self.stopped.set()
            self.running.clear()
            self.terminated.set()
            logger.debug('server: terminated')

    def _find_free_port(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', 0))
            return s.getsockname()[1]


@base.bootstrapped
async def test_verify_controller_cert(event_loop):
    jujudata = FileJujuData()
    controller_name = jujudata.current_controller()
    endpoint = jujudata.controllers()[controller_name]['api-endpoints'][0]
    account = jujudata.accounts()[controller_name]

    my_random_selfsigned_cert = """-----BEGIN CERTIFICATE-----
MIIDBzCCAe+gAwIBAgIUCHZdNBKftmvfofyqx7XM7oEEPFAwDQYJKoZIhvcNAQEL
BQAwEzERMA8GA1UEAwwIY2xpZW50Y2EwHhcNMTkwMjA2MTU1NjMyWhcNMjExMTI2
MTU1NjMyWjATMREwDwYDVQQDDAhjbGllbnRjYTCCASIwDQYJKoZIhvcNAQEBBQAD
ggEPADCCAQoCggEBALS+dI1FngD9Df40Sz6Vdxk3q9Fa+q/rinG257BPwZ8efpKs
gxyiGe+vfaUg6i9ST5uPtra4JeB//8qtebH7UhXpbk+kn3eGRuK56nqPA9QXBJ1X
5WXCkEaT/RuIquV6x8bTy6IqDq83uR15Gdrw6FniLVsNKuumX4yWTBQRDljMYBkm
MJtu/Aliz9885CfVQemqNWu/+XkHS6eCy4A2l1EYxO6YGtyX4hQNfCRLUw7L916k
UdH4Y1Y5L+tD8P2lt1WZVuUcXkAPkhe0dUbCK1wTxj3vy1ASa4JaaszLGIyRPkxH
0M4MGrISDdR36LxaQonGNs6YxphXtslWaSz7jycCAwEAAaNTMFEwHQYDVR0OBBYE
FBbYLQ3o6aleQ4RoVy1ImI73jd3uMB8GA1UdIwQYMBaAFBbYLQ3o6aleQ4RoVy1I
mI73jd3uMA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAHCwhoZZ
F1BsaQpA47Akq1Mvz8y18vYzMGpMQ3X89FG3A+Atyvz87BOAHh3sX0H523T0yN5B
kN7Khl7AzNLGvrolqDBQoi0OlPz+cJkX0DB3LYbn7AJiHdvLB9OFpDta1gV4wUYg
lztYDLJMTf2lXNRLG0ChrvbYoU/As4kcYbQ0ct6H5nxKi0P14PJQZ6b376ru0kIT
Yq2KJhGKIZiGjJ/tekeLkJKR5NLiRZ5AhxYyZKYqK85wPPreMKxWbnDoLWY27FfB
+BmTKcx9ecWtNRFlYVhDW/UXBfL7siP6xQllyJphmO0SKe+vo07ohfSIn3OQVqYn
6wnEIim+TFKbdS0=
-----END CERTIFICATE-----
"""

    try:
        connection = await Connection.connect(
            endpoint=endpoint,
            username=account['user'],
            password=account['password'],
            cacert=my_random_selfsigned_cert,
        )
        await connection.close()
        raise RuntimeError("connection shouldn't be allowed with self signed cert.")
    except ssl.SSLError:
        # All good.
        pass
