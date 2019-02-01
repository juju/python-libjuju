import asyncio
import http
import logging
import socket
import ssl
from contextlib import closing
from pathlib import Path

from juju.client import client
from juju.client.connection import Connection
from juju.controller import Controller
from juju.utils import run_with_interrupt

import pytest
import websockets

from .. import base


logger = logging.getLogger(__name__)


@base.bootstrapped
@pytest.mark.asyncio
async def test_monitor(event_loop):
    async with base.CleanModel() as model:
        conn = model.connection()
        assert conn.monitor.status == 'connected'
        await conn.close()

        assert conn.monitor.status == 'disconnected'


@base.bootstrapped
@pytest.mark.asyncio
async def test_monitor_catches_error(event_loop):

    async with base.CleanModel() as model:
        conn = model.connection()

        assert conn.monitor.status == 'connected'
        try:
            async with conn.monitor.reconnecting:
                await conn.ws.close()
                await asyncio.sleep(1)
                assert conn.monitor.status == 'error'
        finally:
            await conn.close()


@base.bootstrapped
@pytest.mark.asyncio
async def test_full_status(event_loop):
    async with base.CleanModel() as model:
        await model.deploy(
            'ubuntu-0',
            application_name='ubuntu',
            series='trusty',
            channel='stable',
        )

        c = client.ClientFacade.from_connection(model.connection())

        await c.FullStatus(None)


@base.bootstrapped
@pytest.mark.asyncio
async def test_reconnect(event_loop):
    async with base.CleanModel() as model:
        kwargs = model.connection().connect_params()
        conn = await Connection.connect(**kwargs)
        try:
            await asyncio.sleep(0.1)
            assert conn.is_open
            await conn.ws.close()
            assert not conn.is_open
            await model.block_until(lambda: conn.is_open, timeout=3)
        finally:
            await conn.close()


@base.bootstrapped
@pytest.mark.asyncio
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
        http.HTTPStatus.MOVED_PERMANENTLY,
        http.HTTPStatus.FOUND,
        http.HTTPStatus.SEE_OTHER,
        http.HTTPStatus.TEMPORARY_REDIRECT,
        http.HTTPStatus.PERMANENT_REDIRECT,
    ]
    test_server_cert = Path(__file__).with_name('cert.pem')
    kwargs['cacert'] += '\n' + test_server_cert.read_text()
    server = RedirectServer(destination, event_loop)
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
    def __init__(self, destination, loop):
        self.destination = destination
        self.loop = loop
        self._start = asyncio.Event()
        self._stop = asyncio.Event()
        self._terminate = asyncio.Event()
        self.running = asyncio.Event()
        self.stopped = asyncio.Event()
        self.terminated = asyncio.Event()
        if hasattr(ssl, 'PROTOCOL_TLS_SERVER'):
            # python 3.6+
            protocol = ssl.PROTOCOL_TLS_SERVER
        elif hasattr(ssl, 'PROTOCOL_TLS'):
            # python 3.5.3+
            protocol = ssl.PROTOCOL_TLS
        else:
            # python 3.5.2
            protocol = ssl.PROTOCOL_TLSv1_2
        self.ssl_context = ssl.SSLContext(protocol)
        crt_file = Path(__file__).with_name('cert.pem')
        key_file = Path(__file__).with_name('key.pem')
        self.ssl_context.load_cert_chain(str(crt_file), str(key_file))
        self.status = None
        self.port = None
        self._task = self.loop.create_task(self.run())

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
        except (asyncio.CancelledError, asyncio.InvalidStateError):
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
                                         self._terminate,
                                         loop=self.loop)
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
                                                loop=self.loop):
                        self.stopped.clear()
                        self.running.set()
                        logger.debug('server: started')
                        while not self._stop.is_set():
                            await run_with_interrupt(
                                asyncio.sleep(1, loop=self.loop),
                                self._stop,
                                loop=self.loop)
                            logger.debug('server: tick')
                        logger.debug('server: stopping')
                except asyncio.CancelledError:
                    break
                finally:
                    self.stopped.set()
                    self._stop.clear()
                    self.running.clear()
                    logger.debug('server: stopped')
            logger.debug('server: terminating')
        except asyncio.CancelledError:
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
