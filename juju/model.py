import asyncio
import base64
import collections
import hashlib
import json
import logging
import os
import re
import stat
import tempfile
import weakref
import zipfile
from concurrent.futures import CancelledError
from functools import partial
from pathlib import Path

import yaml

import theblues.charmstore
import theblues.errors
import websockets

from . import provisioner, tag, utils
from .annotationhelper import _get_annotations, _set_annotations
from .bundle import BundleHandler, get_charm_series
from .client import client, connector
from .client.client import ConfigValue, Value
from .client.overrides import Caveat, Macaroon
from .constraints import parse as parse_constraints
from .controller import Controller
from .delta import get_entity_class, get_entity_delta
from .errors import JujuAPIError, JujuError
from .exceptions import DeadEntityException
from .names import is_valid_application
from .offerendpoints import ParseError as OfferParseError
from .offerendpoints import parse_local_endpoint, parse_offer_url
from .placement import parse as parse_placement
from .tag import application as application_tag

log = logging.getLogger(__name__)


class _Observer:
    """Wrapper around an observer callable.

    This wrapper allows filter criteria to be associated with the
    callable so that it's only called for changes that meet the criteria.

    """
    def __init__(self, callable_, entity_type, action, entity_id, predicate):
        self.callable_ = callable_
        self.entity_type = entity_type
        self.action = action
        self.entity_id = entity_id
        self.predicate = predicate
        if self.entity_id:
            self.entity_id = str(self.entity_id)
            if not self.entity_id.startswith('^'):
                self.entity_id = '^' + self.entity_id
            if not self.entity_id.endswith('$'):
                self.entity_id += '$'

    async def __call__(self, delta, old, new, model):
        await self.callable_(delta, old, new, model)

    def cares_about(self, delta):
        """Return True if this observer "cares about" (i.e. wants to be
        called) for a this delta.

        """
        if (self.entity_id and delta.get_id() and
                not re.match(self.entity_id, str(delta.get_id()))):
            return False

        if self.entity_type and self.entity_type != delta.entity:
            return False

        if self.action and self.action != delta.type:
            return False

        if self.predicate and not self.predicate(delta):
            return False

        return True


class ModelObserver:
    """
    Base class for creating observers that react to changes in a model.
    """
    async def __call__(self, delta, old, new, model):
        handler_name = 'on_{}_{}'.format(delta.entity, delta.type)
        method = getattr(self, handler_name, self.on_change)
        await method(delta, old, new, model)

    async def on_change(self, delta, old, new, model):
        """Generic model-change handler.

        This should be overridden in a subclass.

        :param delta: :class:`juju.client.overrides.Delta`
        :param old: :class:`juju.model.ModelEntity`
        :param new: :class:`juju.model.ModelEntity`
        :param model: :class:`juju.model.Model`

        """
        pass


class ModelState:
    """Holds the state of the model, including the delta history of all
    entities in the model.

    """
    def __init__(self, model):
        self.model = model
        self.state = dict()

    def _live_entity_map(self, entity_type):
        """Return an id:Entity map of all the living entities of
        type ``entity_type``.

        """
        return {
            entity_id: self.get_entity(entity_type, entity_id)
            for entity_id, history in self.state.get(entity_type, {}).items()
            if history[-1] is not None
        }

    @property
    def applications(self):
        """Return a map of application-name:Application for all applications
        currently in the model.

        """
        return self._live_entity_map('application')

    @property
    def remote_applications(self):
        """Return a map of application-name:Application for all remote
        applications currently in the model.

        """
        return self._live_entity_map('remoteApplication')

    @property
    def application_offers(self):
        """Return a map of application-name:Application for all applications
        offers currently in the model.
        """
        return self._live_entity_map('applicationOffer')

    @property
    def machines(self):
        """Return a map of machine-id:Machine for all machines currently in
        the model.

        """
        return self._live_entity_map('machine')

    @property
    def units(self):
        """Return a map of unit-id:Unit for all units currently in
        the model.

        """
        return self._live_entity_map('unit')

    @property
    def relations(self):
        """Return a map of relation-id:Relation for all relations currently in
        the model.

        """
        return self._live_entity_map('relation')

    def entity_history(self, entity_type, entity_id):
        """Return the history deque for an entity.

        """
        return self.state[entity_type][entity_id]

    def entity_data(self, entity_type, entity_id, history_index):
        """Return the data dict for an entity at a specific index of its
        history.

        """
        return self.entity_history(entity_type, entity_id)[history_index]

    def apply_delta(self, delta):
        """Apply delta to our state and return a copy of the
        affected object as it was before and after the update, e.g.:

            old_obj, new_obj = self.apply_delta(delta)

        old_obj may be None if the delta is for the creation of a new object,
        e.g. a new application or unit is deployed.

        new_obj will never be None, but may be dead (new_obj.dead == True)
        if the object was deleted as a result of the delta being applied.

        """
        history = (
            self.state
            .setdefault(delta.entity, {})
            .setdefault(delta.get_id(), collections.deque())
        )

        history.append(delta.data)
        if delta.type == 'remove':
            history.append(None)

        entity = self.get_entity(delta.entity, delta.get_id())
        return entity.previous(), entity

    def get_entity(
            self, entity_type, entity_id, history_index=-1, connected=True):
        """Return an object instance for the given entity_type and id.

        By default the object state matches the most recent state from
        Juju. To get an instance of the object in an older state, pass
        history_index, an index into the history deque for the entity.

        """

        if history_index < 0 and history_index != -1:
            history_index += len(self.entity_history(entity_type, entity_id))
            if history_index < 0:
                return None

        try:
            self.entity_data(entity_type, entity_id, history_index)
        except IndexError:
            return None

        entity_class = get_entity_class(entity_type)
        return entity_class(
            entity_id, self.model, history_index=history_index,
            connected=connected)


class ModelEntity:
    """An object in the Model tree"""

    def __init__(self, entity_id, model, history_index=-1, connected=True):
        """Initialize a new entity

        :param entity_id str: The unique id of the object in the model
        :param model: The model instance in whose object tree this
            entity resides
        :history_index int: The index of this object's state in the model's
            history deque for this entity
        :connected bool: Flag indicating whether this object gets live updates
            from the model.

        """
        self.entity_id = entity_id
        self.model = model
        self._history_index = history_index
        self.connected = connected
        self.connection = model.connection()

    def __repr__(self):
        return '<{} entity_id="{}">'.format(type(self).__name__,
                                            self.entity_id)

    def __getattr__(self, name):
        """Fetch object attributes from the underlying data dict held in the
        model.

        """
        try:
            return self.safe_data[name]
        except KeyError:
            name = name.replace('_', '-')
            if name in self.safe_data:
                return self.safe_data[name]
            else:
                raise

    def __bool__(self):
        return bool(self.data)

    def on_change(self, callable_):
        """Add a change observer to this entity.

        """
        self.model.add_observer(
            callable_, self.entity_type, 'change', self.entity_id)

    def on_remove(self, callable_):
        """Add a remove observer to this entity.

        """
        self.model.add_observer(
            callable_, self.entity_type, 'remove', self.entity_id)

    @property
    def entity_type(self):
        """A string identifying the entity type of this object, e.g.
        'application' or 'unit', etc.

        """
        def first_lower(s):
            if len(s) == 0:
                return s
            else:
                return s[0].lower() + s[1:]
        return first_lower(self.__class__.__name__)

    @property
    def current(self):
        """Return True if this object represents the current state of the
        entity in the underlying model.

        This will be True except when the object represents an entity at a
        non-latest state in history, e.g. if the object was obtained by calling
        .previous() on another object.

        """
        return self._history_index == -1

    @property
    def dead(self):
        """Returns True if this entity no longer exists in the underlying
        model.

        """
        return (
            self.data is None or
            self.model.state.entity_data(
                self.entity_type, self.entity_id, -1) is None
        )

    @property
    def alive(self):
        """Returns True if this entity still exists in the underlying
        model.

        """
        return not self.dead

    @property
    def data(self):
        """The data dictionary for this entity.

        """
        return self.model.state.entity_data(
            self.entity_type, self.entity_id, self._history_index)

    @property
    def safe_data(self):
        """The data dictionary for this entity.

        If this `ModelEntity` points to the dead state, it will
        raise `DeadEntityException`.

        """
        if self.data is None:
            raise DeadEntityException(
                "Entity {}:{} is dead - its attributes can no longer be "
                "accessed. Use the .previous() method on this object to get "
                "a copy of the object at its previous state.".format(
                    self.entity_type, self.entity_id))
        return self.data

    def previous(self):
        """Return a copy of this object as was at its previous state in
        history.

        Returns None if this object is new (and therefore has no history).

        The returned object is always "disconnected", i.e. does not receive
        live updates.

        """
        return self.model.state.get_entity(
            self.entity_type, self.entity_id, self._history_index - 1,
            connected=False)

    def next(self):
        """Return a copy of this object at its next state in
        history.

        Returns None if this object is already the latest.

        The returned object is "disconnected", i.e. does not receive
        live updates, unless it is current (latest).

        """
        if self._history_index == -1:
            return None

        new_index = self._history_index + 1
        connected = (
            new_index == len(self.model.state.entity_history(
                self.entity_type, self.entity_id)) - 1
        )
        return self.model.state.get_entity(
            self.entity_type, self.entity_id, self._history_index - 1,
            connected=connected)

    def latest(self):
        """Return a copy of this object at its current state in the model.

        Returns self if this object is already the latest.

        The returned object is always "connected", i.e. receives
        live updates from the model.

        """
        if self._history_index == -1:
            return self

        return self.model.state.get_entity(self.entity_type, self.entity_id)


class Model:
    """
    The main API for interacting with a Juju model.
    """
    def __init__(
        self,
        loop=None,
        max_frame_size=None,
        bakery_client=None,
        jujudata=None,
    ):
        """Instantiate a new Model.

        The connect method will need to be called before this
        object can be used for anything interesting.

        If jujudata is None, jujudata.FileJujuData will be used.

        :param loop: an asyncio event loop
        :param max_frame_size: See
            `juju.client.connection.Connection.MAX_FRAME_SIZE`
        :param bakery_client httpbakery.Client: The bakery client to use
            for macaroon authorization.
        :param jujudata JujuData: The source for current controller information
        """
        self._connector = connector.Connector(
            loop=loop,
            max_frame_size=max_frame_size,
            bakery_client=bakery_client,
            jujudata=jujudata,
        )
        self._observers = weakref.WeakValueDictionary()
        self.state = ModelState(self)
        self._info = None
        self._watch_stopping = asyncio.Event(loop=self._connector.loop)
        self._watch_stopped = asyncio.Event(loop=self._connector.loop)
        self._watch_received = asyncio.Event(loop=self._connector.loop)
        self._watch_stopped.set()
        self._charmstore = CharmStore(self._connector.loop)

    def is_connected(self):
        """Reports whether the Model is currently connected."""
        return self._connector.is_connected()

    @property
    def loop(self):
        return self._connector.loop

    def connection(self):
        """Return the current Connection object. It raises an exception
        if the Model is disconnected"""
        return self._connector.connection()

    async def get_controller(self):
        """Return a Controller instance for the currently connected model.
        :return Controller:
        """
        from juju.controller import Controller
        controller = Controller(jujudata=self._connector.jujudata)
        kwargs = self.connection().connect_params()
        kwargs.pop('uuid')
        await controller._connect_direct(**kwargs)
        return controller

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    async def connect(self, *args, **kwargs):
        """Connect to a juju model.

        This supports two calling conventions:

        The model and (optionally) authentication information can be taken
        from the data files created by the Juju CLI.  This convention will
        be used if a ``model_name`` is specified, or if the ``endpoint``
        and ``uuid`` are not.

        Otherwise, all of the ``endpoint``, ``uuid``, and authentication
        information (``username`` and ``password``, or ``bakery_client`` and/or
        ``macaroons``) are required.

        If a single positional argument is given, it will be assumed to be
        the ``model_name``.  Otherwise, the first positional argument, if any,
        must be the ``endpoint``.

        Available parameters are:

        :param model_name:  Format [controller:][user/]model
        :param str endpoint: The hostname:port of the controller to connect to.
        :param str uuid: The model UUID to connect to.
        :param str username: The username for controller-local users (or None
            to use macaroon-based login.)
        :param str password: The password for controller-local users.
        :param str cacert: The CA certificate of the controller
            (PEM formatted).
        :param httpbakery.Client bakery_client: The macaroon bakery client to
            to use when performing macaroon-based login. Macaroon tokens
            acquired when logging will be saved to bakery_client.cookies.
            If this is None, a default bakery_client will be used.
        :param list macaroons: List of macaroons to load into the
            ``bakery_client``.
        :param asyncio.BaseEventLoop loop: The event loop to use for async
            operations.
        :param int max_frame_size: The maximum websocket frame size to allow.
        :param specified_facades: Overwrite the facades with a series of
            specified facades.
        """
        await self.disconnect()
        if 'endpoint' not in kwargs and len(args) < 2:
            if args and 'model_name' in kwargs:
                raise TypeError('connect() got multiple values for model_name')
            elif args:
                model_name = args[0]
            else:
                model_name = kwargs.pop('model_name', None)
            await self._connector.connect_model(model_name, **kwargs)
        else:
            if 'model_name' in kwargs:
                raise TypeError('connect() got values for both '
                                'model_name and endpoint')
            if args and 'endpoint' in kwargs:
                raise TypeError('connect() got multiple values for endpoint')
            if len(args) < 2 and 'uuid' not in kwargs:
                raise TypeError('connect() missing value for uuid')
            has_userpass = (len(args) >= 4 or
                            {'username', 'password'}.issubset(kwargs))
            has_macaroons = (len(args) >= 6 or not
                             {'bakery_client', 'macaroons'}.isdisjoint(kwargs))
            if not (has_userpass or has_macaroons):
                raise TypeError('connect() missing auth params')
            arg_names = [
                'endpoint',
                'uuid',
                'username',
                'password',
                'cacert',
                'bakery_client',
                'macaroons',
                'loop',
                'max_frame_size',
            ]
            for i, arg in enumerate(args):
                kwargs[arg_names[i]] = arg
            if not {'endpoint', 'uuid'}.issubset(kwargs):
                raise ValueError('endpoint and uuid are required '
                                 'if model_name not given')
            if not ({'username', 'password'}.issubset(kwargs) or
                    {'bakery_client', 'macaroons'}.intersection(kwargs)):
                raise ValueError('Authentication parameters are required '
                                 'if model_name not given')
            await self._connector.connect(**kwargs)
        await self._after_connect()

    async def connect_model(self, model_name):
        """
        .. deprecated:: 0.6.2
           Use ``connect(model_name=model_name)`` instead.
        """
        return await self.connect(model_name=model_name)

    async def connect_current(self):
        """
        .. deprecated:: 0.6.2
           Use ``connect()`` instead.
        """
        return await self.connect()

    async def _connect_direct(self, **kwargs):
        await self.disconnect()
        await self._connector.connect(**kwargs)
        await self._after_connect()

    async def _after_connect(self):
        self._watch()

        # Wait for the first packet of data from the AllWatcher,
        # which contains all information on the model.
        # TODO this means that we can't do anything until
        # we've received all the model data, which might be
        # a whole load of unneeded data if all the client wants
        # to do is make one RPC call.
        await self._watch_received.wait()

        await self.get_info()
        self.uuid = self.info.uuid

    async def disconnect(self):
        """Shut down the watcher task and close websockets.

        """
        if not self._watch_stopped.is_set():
            log.debug('Stopping watcher task')
            self._watch_stopping.set()
            await self._watch_stopped.wait()
            self._watch_stopping.clear()

        if self.is_connected():
            log.debug('Closing model connection')
            await self._connector.disconnect()
            self._info = None

    async def add_local_charm_dir(self, charm_dir, series):
        """Upload a local charm to the model.

        This will automatically generate an archive from
        the charm dir.

        :param charm_dir: Path to the charm directory
        :param series: Charm series

        """
        fh = tempfile.NamedTemporaryFile()
        CharmArchiveGenerator(charm_dir).make_archive(fh.name)
        with fh:
            func = partial(
                self.add_local_charm, fh, series, os.stat(fh.name).st_size)
            charm_url = await self._connector.loop.run_in_executor(None, func)

        log.debug('Uploaded local charm: %s -> %s', charm_dir, charm_url)
        return charm_url

    def add_local_charm(self, charm_file, series, size=None):
        """Upload a local charm archive to the model.

        Returns the 'local:...' url that should be used to deploy the charm.

        :param charm_file: Path to charm zip archive
        :param series: Charm series
        :param size: Size of the archive, in bytes
        :return str: 'local:...' url for deploying the charm
        :raises: :class:`JujuError` if the upload fails

        Uses an https endpoint at the same host:port as the wss.
        Supports large file uploads.

        .. warning::

           This method will block. Consider using :meth:`add_local_charm_dir`
           instead.

        """
        conn, headers, path_prefix = self.connection().https_connection()
        path = "%s/charms?series=%s" % (path_prefix, series)
        headers['Content-Type'] = 'application/zip'
        if size:
            headers['Content-Length'] = size
        conn.request("POST", path, charm_file, headers)
        response = conn.getresponse()
        result = response.read().decode()
        if not response.status == 200:
            raise JujuError(result)
        result = json.loads(result)
        return result['charm-url']

    def all_units_idle(self):
        """Return True if all units are idle.

        """
        for unit in self.units.values():
            unit_status = unit.data['agent-status']['current']
            if unit_status != 'idle':
                return False
        return True

    async def reset(self, force=False):
        """Reset the model to a clean state.

        :param bool force: Force-terminate machines.

        This returns only after the model has reached a clean state. "Clean"
        means no applications or machines exist in the model.

        """
        log.debug('Resetting model')
        for app in self.applications.values():
            await app.destroy()
        for machine in self.machines.values():
            await machine.destroy(force=force)
        await self.block_until(
            lambda: len(self.machines) == 0
        )

    async def block_until(self, *conditions, timeout=None, wait_period=0.5):
        """Return only after all conditions are true.

        Raises `websockets.ConnectionClosed` if disconnected.
        """
        def _disconnected():
            return not (self.is_connected() and self.connection().is_open)

        def done():
            return _disconnected() or all(c() for c in conditions)

        await utils.block_until(done,
                                timeout=timeout,
                                wait_period=wait_period,
                                loop=self.loop)
        if _disconnected():
            raise websockets.ConnectionClosed(1006, 'no reason')

    @property
    def tag(self):
        return tag.model(self.uuid)

    @property
    def applications(self):
        """Return a map of application-name:Application for all applications
        currently in the model.

        """
        return self.state.applications

    @property
    def remote_applications(self):
        """Return a map of application-name:Application for all remote
        applications currently in the model.

        """
        return self.state.remote_applications

    @property
    def application_offers(self):
        """Return a map of application-name:Application for all applications
        offers currently in the model.
        """
        return self.state.application_offers

    @property
    def machines(self):
        """Return a map of machine-id:Machine for all machines currently in
        the model.

        """
        return self.state.machines

    @property
    def units(self):
        """Return a map of unit-id:Unit for all units currently in
        the model.

        """
        return self.state.units

    @property
    def relations(self):
        """Return a list of all Relations currently in the model.

        """
        return list(self.state.relations.values())

    async def get_info(self):
        """Return a client.ModelInfo object for this Model.

        Retrieves latest info for this Model from the api server. The
        return value is cached on the Model.info attribute so that the
        valued may be accessed again without another api call, if
        desired.

        This method is called automatically when the Model is connected,
        resulting in Model.info being initialized without requiring an
        explicit call to this method.

        """
        facade = client.ClientFacade.from_connection(self.connection())

        self._info = await facade.ModelInfo()
        log.debug('Got ModelInfo: %s', vars(self.info))

        return self.info

    @property
    def info(self):
        """Return the cached client.ModelInfo object for this Model.

        If Model.get_info() has not been called, this will return None.
        """
        return self._info

    def add_observer(
            self, callable_, entity_type=None, action=None, entity_id=None,
            predicate=None):
        """Register an "on-model-change" callback

        Once the model is connected, ``callable_``
        will be called each time the model changes. ``callable_`` should
        be Awaitable and accept the following positional arguments:

            delta - An instance of :class:`juju.delta.EntityDelta`
                containing the raw delta data recv'd from the Juju
                websocket.

            old_obj - If the delta modifies an existing object in the model,
                old_obj will be a copy of that object, as it was before the
                delta was applied. Will be None if the delta creates a new
                entity in the model.

            new_obj - A copy of the new or updated object, after the delta
                is applied. Will be None if the delta removes an entity
                from the model.

            model - The :class:`Model` itself.

        Events for which ``callable_`` is called can be specified by passing
        entity_type, action, and/or entitiy_id filter criteria, e.g.::

            add_observer(
                myfunc,
                entity_type='application', action='add', entity_id='ubuntu')

        For more complex filtering conditions, pass a predicate function. It
        will be called with a delta as its only argument. If the predicate
        function returns True, the ``callable_`` will be called.

        """
        observer = _Observer(
            callable_, entity_type, action, entity_id, predicate)
        self._observers[observer] = callable_

    def _watch(self):
        """Start an asynchronous watch against this model.

        See :meth:`add_observer` to register an onchange callback.

        """
        async def _all_watcher():
            try:
                allwatcher = client.AllWatcherFacade.from_connection(
                    self.connection())
                while not self._watch_stopping.is_set():
                    try:
                        results = await utils.run_with_interrupt(
                            allwatcher.Next(),
                            self._watch_stopping,
                            loop=self._connector.loop)
                    except JujuAPIError as e:
                        if 'watcher was stopped' not in str(e):
                            raise
                        if self._watch_stopping.is_set():
                            # this shouldn't ever actually happen, because
                            # the event should trigger before the controller
                            # has a chance to tell us the watcher is stopped
                            # but handle it gracefully, just in case
                            break
                        # controller stopped our watcher for some reason
                        # but we're not actually stopping, so just restart it
                        log.warning(
                            'Watcher: watcher stopped, restarting')
                        del allwatcher.Id
                        continue
                    except websockets.ConnectionClosed:
                        monitor = self.connection().monitor
                        if monitor.status == monitor.ERROR:
                            # closed unexpectedly, try to reopen
                            log.warning(
                                'Watcher: connection closed, reopening')
                            await self.connection().reconnect()
                            if monitor.status != monitor.CONNECTED:
                                # reconnect failed; abort and shutdown
                                log.error('Watcher: automatic reconnect '
                                          'failed; stopping watcher')
                                break
                            del allwatcher.Id
                            continue
                        else:
                            # closed on request, go ahead and shutdown
                            break
                    if self._watch_stopping.is_set():
                        try:
                            await allwatcher.Stop()
                        except websockets.ConnectionClosed:
                            pass  # can't stop on a closed conn
                        break
                    for delta in results.deltas:
                        try:
                            delta = get_entity_delta(delta)
                            old_obj, new_obj = self.state.apply_delta(delta)
                            await self._notify_observers(delta, old_obj, new_obj)
                        except KeyError as e:
                            # TODO (stickupkid): we should raise the unknown delta
                            # type, so we handle correctly all the types comming from
                            # the all watcher. Currently they're ignored, causing
                            # issue.
                            # raise JujuError("unknown delta type {}".format(e.args))
                            log.warning("unknown delta type: %s", e.args[0])
                    self._watch_received.set()
            except CancelledError:
                pass
            except Exception:
                log.exception('Error in watcher')
                raise
            finally:
                self._watch_stopped.set()

        log.debug('Starting watcher task')
        self._watch_received.clear()
        self._watch_stopping.clear()
        self._watch_stopped.clear()
        self._connector.loop.create_task(_all_watcher())

    async def _notify_observers(self, delta, old_obj, new_obj):
        """Call observing callbacks, notifying them of a change in model state

        :param delta: The raw change from the watcher
            (:class:`juju.client.overrides.Delta`)
        :param old_obj: The object in the model that this delta updates.
            May be None.
        :param new_obj: The object in the model that is created or updated
            by applying this delta.

        """
        if new_obj and not old_obj:
            delta.type = 'add'

        log.debug(
            'Model changed: %s %s %s',
            delta.entity, delta.type, delta.get_id())

        for o in self._observers:
            if o.cares_about(delta):
                asyncio.ensure_future(o(delta, old_obj, new_obj, self),
                                      loop=self._connector.loop)

    async def _wait(self, entity_type, entity_id, action, predicate=None):
        """
        Block the calling routine until a given action has happened to the
        given entity

        :param entity_type: The entity's type.
        :param entity_id: The entity's id.
        :param action: the type of action (e.g., 'add', 'change', or 'remove')
        :param predicate: optional callable that must take as an
            argument a delta, and must return a boolean, indicating
            whether the delta contains the specific action we're looking
            for. For example, you might check to see whether a 'change'
            has a 'completed' status. See the _Observer class for details.

        """
        q = asyncio.Queue(loop=self._connector.loop)

        async def callback(delta, old, new, model):
            await q.put(delta.get_id())

        self.add_observer(callback, entity_type, action, entity_id, predicate)
        entity_id = await q.get()
        # object might not be in the entity_map if we were waiting for a
        # 'remove' action
        return self.state._live_entity_map(entity_type).get(entity_id)

    async def _wait_for_new(self, entity_type, entity_id):
        """Wait for a new object to appear in the Model and return it.

        Waits for an object of type ``entity_type`` with id ``entity_id``
        to appear in the model.  This is similar to watching for the
        object using ``block_until``, but uses the watcher rather than
        polling.

        """
        # if the entity is already in the model, just return it
        if entity_id in self.state._live_entity_map(entity_type):
            return self.state._live_entity_map(entity_type)[entity_id]
        return await self._wait(entity_type, entity_id, None)

    async def wait_for_action(self, action_id):
        """Given an action, wait for it to complete."""

        if action_id.startswith("action-"):
            # if we've been passed action.tag, transform it into the
            # id that the api deltas will use.
            action_id = action_id[7:]

        def predicate(delta):
            return delta.data['status'] in ('completed', 'failed')

        return await self._wait('action', action_id, None, predicate)

    async def get_annotations(self):
        """Get annotations on this model.

        :return dict: The annotations for this model
        """
        return await _get_annotations(self.tag, self.connection())

    async def set_annotations(self, annotations):
        """Set annotations on this model.

        :param annotations map[string]string: the annotations as key/value
            pairs.

        """
        return await _set_annotations(self.tag, annotations, self.connection())

    async def add_machine(
            self, spec=None, constraints=None, disks=None, series=None):
        """Start a new, empty machine and optionally a container, or add a
        container to a machine.

        :param str spec: Machine specification
            Examples::

                (None) - starts a new machine
                'lxd' - starts a new machine with one lxd container
                'lxd:4' - starts a new lxd container on machine 4
                'ssh:user@10.10.0.3:/path/to/private/key' - manually provision
                a machine with ssh and the private key used for authentication
                'zone=us-east-1a' - starts a machine in zone us-east-1s on AWS
                'maas2.name' - acquire machine maas2.name on MAAS

        :param dict constraints: Machine constraints, which can contain the
            the following keys::

                arch : str
                container : str
                cores : int
                cpu_power : int
                instance_type : str
                mem : int
                root_disk : int
                spaces : list(str)
                tags : list(str)
                virt_type : str

            Example::

                constraints={
                    'mem': 256 * MB,
                    'tags': ['virtual'],
                }

        :param list disks: List of disk constraint dictionaries, which can
            contain the following keys::

                count : int
                pool : str
                size : int

            Example::

                disks=[{
                    'pool': 'rootfs',
                    'size': 10 * GB,
                    'count': 1,
                }]

        :param str series: Series, e.g. 'xenial'

        Supported container types are: lxd, kvm

        When deploying a container to an existing machine, constraints cannot
        be used.

        """
        params = client.AddMachineParams()

        if spec:
            if spec.startswith("ssh:"):
                placement, target, private_key_path = spec.split(":")
                user, host = target.split("@")

                sshProvisioner = provisioner.SSHProvisioner(
                    host=host,
                    user=user,
                    private_key_path=private_key_path,
                )

                params = sshProvisioner.provision_machine()
            else:
                placement = parse_placement(spec)
                if placement:
                    params.placement = placement[0]

        params.jobs = ['JobHostUnits']

        if constraints:
            params.constraints = client.Value.from_json(constraints)

        if disks:
            params.disks = [
                client.Constraints.from_json(o) for o in disks]

        if series:
            params.series = series

        # Submit the request.
        client_facade = client.ClientFacade.from_connection(self.connection())
        results = await client_facade.AddMachines(params=[params])
        error = results.machines[0].error
        if error:
            raise ValueError("Error adding machine: %s" % error.message)
        machine_id = results.machines[0].machine

        if spec:
            if spec.startswith("ssh:"):
                # Need to run this after AddMachines has been called,
                # as we need the machine_id
                await sshProvisioner.install_agent(
                    self.connection(),
                    params.nonce,
                    machine_id,
                )

        log.debug('Added new machine %s', machine_id)
        return await self._wait_for_new('machine', machine_id)

    async def add_relation(self, relation1, relation2):
        """Add a relation between two applications.

        :param str relation1: '<application>[:<relation_name>]'
        :param str relation2: '<application>[:<relation_name>]'

        """
        # attempt to validate any url that are passed in.
        endpoints = []
        remote_endpoint = None
        for ep in [relation1, relation2]:
            try:
                url = parse_offer_url(ep)
            except OfferParseError:
                pass
            else:
                if remote_endpoint is not None:
                    raise JujuError("move than one remote endpoints not supported")
                remote_endpoint = url
                endpoints.append(url.application)
                continue

            try:
                parse_local_endpoint(ep)
            except OfferParseError:
                raise
            else:
                endpoints.append(ep)
        if len(endpoints) != 2:
            raise JujuError("error validating one of the endpoints")

        facade_cls = client.ApplicationFacade
        if remote_endpoint is not None:
            if facade_cls.best_facade_version(self.connection()) < 5:
                # old clients don't support cross model capability
                raise JujuError("cannot add relation to {}: remote endpoints not supported".format(remote_endpoint.string()))

            if remote_endpoint.has_empty_source():
                current = await self.get_controller()
                remote_endpoint.source = current.controller_name
            # consume the remote endpoint
            await self.consume(remote_endpoint.string(),
                               application_alias=remote_endpoint.application,
                               controller_name=remote_endpoint.source)

        log.debug(
            'Adding relation %s <-> %s', endpoints[0], endpoints[1])

        def _find_relation(*specs):
            for rel in self.relations:
                if rel.matches(*specs):
                    return rel
            return None

        app_facade = facade_cls.from_connection(self.connection())
        try:
            result = await app_facade.AddRelation(endpoints=endpoints, via_cidrs=None)
        except JujuAPIError as e:
            if 'relation already exists' not in e.message:
                raise
            rel = _find_relation(endpoints[0], endpoints[1])
            if rel:
                return rel
            raise JujuError('Relation {} {} exists but not in model'.format(
                endpoints[0], endpoints[1]))

        specs = ['{}:{}'.format(app, data['name'])
                 for app, data in result.endpoints.items()]

        await self.block_until(lambda: _find_relation(*specs) is not None)
        return _find_relation(*specs)

    def add_space(self, name, *cidrs):
        """Add a new network space.

        Adds a new space with the given name and associates the given
        (optional) list of existing subnet CIDRs with it.

        :param str name: Name of the space
        :param *cidrs: Optional list of existing subnet CIDRs

        """
        raise NotImplementedError()

    async def add_ssh_key(self, user, key):
        """Add a public SSH key to this model.

        :param str user: The username of the user
        :param str key: The public ssh key

        """
        key_facade = client.KeyManagerFacade.from_connection(self.connection())
        return await key_facade.AddKeys(ssh_keys=[key], user=user)
    add_ssh_keys = add_ssh_key

    def add_subnet(self, cidr_or_id, space, *zones):
        """Add an existing subnet to this model.

        :param str cidr_or_id: CIDR or provider ID of the existing subnet
        :param str space: Network space with which to associate
        :param str *zones: Zone(s) in which the subnet resides

        """
        raise NotImplementedError()

    def get_backups(self):
        """Retrieve metadata for backups in this model.

        """
        raise NotImplementedError()

    def block(self, *commands):
        """Add a new block to this model.

        :param str *commands: The commands to block. Valid values are
            'all-changes', 'destroy-model', 'remove-object'

        """
        raise NotImplementedError()

    def get_blocks(self):
        """List blocks for this model.

        """
        raise NotImplementedError()

    def get_cached_images(self, arch=None, kind=None, series=None):
        """Return a list of cached OS images.

        :param str arch: Filter by image architecture
        :param str kind: Filter by image kind, e.g. 'lxd'
        :param str series: Filter by image series, e.g. 'xenial'

        """
        raise NotImplementedError()

    def create_backup(self, note=None, no_download=False):
        """Create a backup of this model.

        :param str note: A note to store with the backup
        :param bool no_download: Do not download the backup archive
        :return str: Path to downloaded archive

        """
        raise NotImplementedError()

    def create_storage_pool(self, name, provider_type, **pool_config):
        """Create or define a storage pool.

        :param str name: Name to give the storage pool
        :param str provider_type: Pool provider type
        :param **pool_config: key/value pool configuration pairs

        """
        raise NotImplementedError()

    def debug_log(
            self, no_tail=False, exclude_module=None, include_module=None,
            include=None, level=None, limit=0, lines=10, replay=False,
            exclude=None):
        """Get log messages for this model.

        :param bool no_tail: Stop after returning existing log messages
        :param list exclude_module: Do not show log messages for these logging
            modules
        :param list include_module: Only show log messages for these logging
            modules
        :param list include: Only show log messages for these entities
        :param str level: Log level to show, valid options are 'TRACE',
            'DEBUG', 'INFO', 'WARNING', 'ERROR,
        :param int limit: Return this many of the most recent (possibly
            filtered) lines are shown
        :param int lines: Yield this many of the most recent lines, and keep
            yielding
        :param bool replay: Yield the entire log, and keep yielding
        :param list exclude: Do not show log messages for these entities

        """
        raise NotImplementedError()

    def _get_series(self, entity_url, entity):
        # try to get the series from the provided charm URL
        if entity_url.startswith('cs:'):
            parts = entity_url[3:].split('/')
        else:
            parts = entity_url.split('/')
        if parts[0].startswith('~'):
            parts.pop(0)
        if len(parts) > 1:
            # series was specified in the URL
            return parts[0]
        # series was not supplied at all, so use the newest
        # supported series according to the charm store
        ss = entity['Meta']['supported-series']
        return ss['SupportedSeries'][0]

    async def deploy(
            self, entity_url, application_name=None, bind=None, budget=None,
            channel=None, config=None, constraints=None, force=False,
            num_units=1, plan=None, resources=None, series=None, storage=None,
            to=None, devices=None, trust=False):
        """Deploy a new service or bundle.

        :param str entity_url: Charm or bundle url
        :param str application_name: Name to give the service
        :param dict bind: <charm endpoint>:<network space> pairs
        :param dict budget: <budget name>:<limit> pairs
        :param str channel: Charm store channel from which to retrieve
            the charm or bundle, e.g. 'edge'
        :param dict config: Charm configuration dictionary
        :param constraints: Service constraints
        :type constraints: :class:`juju.Constraints`
        :param bool force: Allow charm to be deployed to a machine running
            an unsupported series
        :param int num_units: Number of units to deploy
        :param str plan: Plan under which to deploy charm
        :param dict resources: <resource name>:<file path> pairs
        :param str series: Series on which to deploy
        :param dict storage: Storage constraints TODO how do these look?
        :param to: Placement directive as a string. For example:

            '23' - place on machine 23
            'lxd:7' - place in new lxd container on machine 7
            '24/lxd/3' - place in container 3 on machine 24

            If None, a new machine is provisioned.
        :param bool trust: Trust signifies that the charm should be deployed
            with access to trusted credentials. Hooks run by the charm can access
            cloud credentials and other trusted access credentials.

        TODO::

            - support local resources

        """
        if storage:
            storage = {
                k: client.Constraints(**v)
                for k, v in storage.items()
            }
        if trust and (self.info.agent_version < client.Number.from_json('2.4.0')):
            raise NotImplementedError("trusted is not supported on model version {}".format(self.info.agent_version))

        entity_path = Path(entity_url.replace('local:', ''))
        bundle_path = entity_path / 'bundle.yaml'
        metadata_path = entity_path / 'metadata.yaml'

        is_local = (
            entity_url.startswith('local:') or
            entity_path.is_dir() or
            entity_path.is_file()
        )
        if is_local:
            entity_id = entity_url.replace('local:', '')
        else:
            entity = await self.charmstore.entity(entity_url, channel=channel,
                                                  include_stats=False)
            entity_id = entity['Id']

        client_facade = client.ClientFacade.from_connection(self.connection())

        is_bundle = ((is_local and
                      (entity_id.endswith('.yaml') and entity_path.exists()) or
                      bundle_path.exists()) or
                     (not is_local and 'bundle/' in entity_id))

        if is_bundle:
            handler = BundleHandler(self, trusted=trust, forced=force)
            await handler.fetch_plan(entity_id)
            await handler.execute_plan()
            extant_apps = {app for app in self.applications}
            pending_apps = set(handler.applications) - extant_apps
            if pending_apps:
                # new apps will usually be in the model by now, but if some
                # haven't made it yet we'll need to wait on them to be added
                await asyncio.gather(*[
                    asyncio.ensure_future(
                        self._wait_for_new('application', app_name),
                        loop=self._connector.loop)
                    for app_name in pending_apps
                ], loop=self._connector.loop)
            return [app for name, app in self.applications.items()
                    if name in handler.applications]
        else:
            if not is_local:
                if not application_name:
                    application_name = entity['Meta']['charm-metadata']['Name']
                if not series:
                    series = self._get_series(entity_url, entity)
                await client_facade.AddCharm(channel=channel, url=entity_id, force=False)
                # XXX: we're dropping local resources here, but we don't
                # actually support them yet anyway
                resources = await self._add_store_resources(application_name,
                                                            entity_id,
                                                            entity=entity)
            else:
                if not application_name:
                    metadata = yaml.load(metadata_path.read_text(), Loader=yaml.FullLoader)
                    application_name = metadata['name']
                # We have a local charm dir that needs to be uploaded
                charm_dir = os.path.abspath(
                    os.path.expanduser(entity_id))
                series = series or get_charm_series(charm_dir)
                if not series:
                    raise JujuError(
                        "Couldn't determine series for charm at {}. "
                        "Pass a 'series' kwarg to Model.deploy().".format(
                            charm_dir))
                entity_id = await self.add_local_charm_dir(charm_dir, series)
            if config is None:
                config = {}
            if trust:
                config["trust"] = "true"
            return await self._deploy(
                charm_url=entity_id,
                application=application_name,
                series=series,
                config=config,
                constraints=constraints,
                endpoint_bindings=bind,
                resources=resources,
                storage=storage,
                channel=channel,
                num_units=num_units,
                placement=parse_placement(to),
                devices=devices,
            )

    async def _add_store_resources(self, application, entity_url,
                                   overrides=None, entity=None):
        if not entity:
            # avoid extra charm store call if one was already made
            entity = await self.charmstore.entity(entity_url,
                                                  include_stats=False)
        resources = [
            {
                'description': resource['Description'],
                'fingerprint': resource['Fingerprint'],
                'name': resource['Name'],
                'path': resource['Path'],
                'revision': resource['Revision'],
                'size': resource['Size'],
                'type_': resource['Type'],
                'origin': 'store',
            } for resource in entity['Meta']['resources']
        ]

        if overrides:
            names = {r['name'] for r in resources}
            unknown = overrides.keys() - names
            if unknown:
                raise JujuError('Unrecognized resource{}: {}'.format(
                    's' if len(unknown) > 1 else '',
                    ', '.join(unknown)))
            for resource in resources:
                if resource['name'] in overrides:
                    resource['revision'] = overrides[resource['name']]

        if not resources:
            return None

        resources_facade = client.ResourcesFacade.from_connection(
            self.connection())
        response = await resources_facade.AddPendingResources(
            application_tag=tag.application(application),
            charm_url=entity_url,
            resources=[client.CharmResource(**resource) for resource in resources])
        resource_map = {resource['name']: pid
                        for resource, pid
                        in zip(resources, response.pending_ids)}
        return resource_map

    async def _deploy(self, charm_url, application, series, config,
                      constraints, endpoint_bindings, resources, storage,
                      channel=None, num_units=None, placement=None,
                      devices=None):
        """Logic shared between `Model.deploy` and `BundleHandler.deploy`.
        """
        log.info('Deploying %s', charm_url)

        # stringify all config values for API, and convert to YAML
        config = {k: str(v) for k, v in config.items()}
        config = yaml.dump({application: config},
                           default_flow_style=False)

        app_facade = client.ApplicationFacade.from_connection(
            self.connection())

        app = client.ApplicationDeploy(
            charm_url=charm_url,
            application=application,
            series=series,
            channel=channel,
            config_yaml=config,
            constraints=parse_constraints(constraints),
            endpoint_bindings=endpoint_bindings,
            num_units=num_units,
            resources=resources,
            storage=storage,
            placement=placement,
            devices=devices,
        )
        result = await app_facade.Deploy(applications=[app])
        errors = [r.error.message for r in result.results if r.error]
        if errors:
            raise JujuError('\n'.join(errors))
        return await self._wait_for_new('application', application)

    async def destroy(self):
        """Terminate all machines and resources for this model.
            Is already implemented in controller.py.
        """
        raise NotImplementedError()

    async def destroy_unit(self, *unit_names):
        """Destroy units by name.

        """
        connection = self.connection()
        app_facade = client.ApplicationFacade.from_connection(connection)

        log.debug(
            'Destroying unit%s %s',
            's' if len(unit_names) == 1 else '',
            ' '.join(unit_names))

        return await app_facade.DestroyUnits(unit_names=list(unit_names))
    destroy_units = destroy_unit

    def get_backup(self, archive_id):
        """Download a backup archive file.

        :param str archive_id: The id of the archive to download
        :return str: Path to the archive file

        """
        raise NotImplementedError()

    def enable_ha(
            self, num_controllers=0, constraints=None, series=None, to=None):
        """Ensure sufficient controllers exist to provide redundancy.

        :param int num_controllers: Number of controllers to make available
        :param constraints: Constraints to apply to the controller machines
        :type constraints: :class:`juju.Constraints`
        :param str series: Series of the controller machines
        :param list to: Placement directives for controller machines, e.g.::

            '23' - machine 23
            'lxc:7' - new lxc container on machine 7
            '24/lxc/3' - lxc container 3 or machine 24

            If None, a new machine is provisioned.

        """
        raise NotImplementedError()

    async def get_config(self):
        """Return the configuration settings for this model.

        :returns: A ``dict`` mapping keys to `ConfigValue` instances,
            which have `source` and `value` attributes.
        """
        config_facade = client.ModelConfigFacade.from_connection(
            self.connection()
        )
        result = await config_facade.ModelGet()
        config = result.config
        for key, value in config.items():
            config[key] = ConfigValue.from_json(value)
        return config

    async def get_constraints(self):
        """Return the machine constraints for this model.

        :returns: A ``dict`` of constraints.
        """
        constraints = {}
        client_facade = client.ClientFacade.from_connection(self.connection())
        result = await client_facade.GetModelConstraints()

        # GetModelConstraints returns GetConstraintsResults which has a
        # 'constraints' attribute. If no constraints have been set
        # GetConstraintsResults.constraints is None. Otherwise
        # GetConstraintsResults.constraints has an attribute for each possible
        # constraint, each of these in turn will be None if they have not been
        # set.
        if result.constraints:
            constraint_types = [a for a in dir(result.constraints)
                                if a in Value._toSchema.keys()]
            for constraint in constraint_types:
                value = getattr(result.constraints, constraint)
                if value is not None:
                    constraints[constraint] = getattr(result.constraints,
                                                      constraint)
        return constraints

    def import_ssh_key(self, identity):
        """Add a public SSH key from a trusted indentity source to this model.

        :param str identity: User identity in the form <lp|gh>:<username>

        """
        raise NotImplementedError()
    import_ssh_keys = import_ssh_key

    async def get_machines(self):
        """Return list of machines in this model.

        """
        return list(self.state.machines.keys())

    def get_shares(self):
        """Return list of all users with access to this model.

        """
        raise NotImplementedError()

    def get_spaces(self):
        """Return list of all known spaces, including associated subnets.

        """
        raise NotImplementedError()

    async def get_ssh_key(self, raw_ssh=False):
        """Return known SSH keys for this model.
        :param bool raw_ssh: if True, returns the raw ssh key,
            else it's fingerprint

        """
        key_facade = client.KeyManagerFacade.from_connection(self.connection())
        entity = {'tag': tag.model(self.info.uuid)}
        entities = client.Entities([entity])
        return await key_facade.ListKeys(entities=entities, mode=raw_ssh)
    get_ssh_keys = get_ssh_key

    def get_storage(self, filesystem=False, volume=False):
        """Return details of storage instances.

        :param bool filesystem: Include filesystem storage
        :param bool volume: Include volume storage

        """
        raise NotImplementedError()

    def get_storage_pools(self, names=None, providers=None):
        """Return list of storage pools.

        :param list names: Only include pools with these names
        :param list providers: Only include pools for these providers

        """
        raise NotImplementedError()

    def get_subnets(self, space=None, zone=None):
        """Return list of known subnets.

        :param str space: Only include subnets in this space
        :param str zone: Only include subnets in this zone

        """
        raise NotImplementedError()

    def remove_blocks(self):
        """Remove all blocks from this model.

        """
        raise NotImplementedError()

    def remove_backup(self, backup_id):
        """Delete a backup.

        :param str backup_id: The id of the backup to remove

        """
        raise NotImplementedError()

    def remove_cached_images(self, arch=None, kind=None, series=None):
        """Remove cached OS images.

        :param str arch: Architecture of the images to remove
        :param str kind: Image kind to remove, e.g. 'lxd'
        :param str series: Image series to remove, e.g. 'xenial'

        """
        raise NotImplementedError()

    def remove_machine(self, *machine_ids):
        """Remove a machine from this model.

        :param str *machine_ids: Ids of the machines to remove

        """
        raise NotImplementedError()
    remove_machines = remove_machine

    async def remove_ssh_key(self, user, key):
        """Remove a public SSH key(s) from this model.

        :param str key: Full ssh key
        :param str user: Juju user to which the key is registered

        """
        key_facade = client.KeyManagerFacade.from_connection(self.connection())
        key = base64.b64decode(bytes(key.strip().split()[1].encode('ascii')))
        key = hashlib.md5(key).hexdigest()
        key = ':'.join(a + b for a, b in zip(key[::2], key[1::2]))
        await key_facade.DeleteKeys(ssh_keys=[key], user=user)
    remove_ssh_keys = remove_ssh_key

    def restore_backup(
            self, bootstrap=False, constraints=None, archive=None,
            backup_id=None, upload_tools=False):
        """Restore a backup archive to a new controller.

        :param bool bootstrap: Bootstrap a new state machine
        :param constraints: Model constraints
        :type constraints: :class:`juju.Constraints`
        :param str archive: Path to backup archive to restore
        :param str backup_id: Id of backup to restore
        :param bool upload_tools: Upload tools if bootstrapping a new machine

        """
        raise NotImplementedError()

    def retry_provisioning(self):
        """Retry provisioning for failed machines.

        """
        raise NotImplementedError()

    def run(self, command, timeout=None):
        """Run command on all machines in this model.

        :param str command: The command to run
        :param int timeout: Time to wait before command is considered failed

        """
        raise NotImplementedError()

    async def set_config(self, config):
        """Set configuration keys on this model.

        :param dict config: Mapping of config keys to either string values or
            `ConfigValue` instances, as returned by `get_config`.
        """
        config_facade = client.ModelConfigFacade.from_connection(
            self.connection()
        )
        for key, value in config.items():
            if isinstance(value, ConfigValue):
                config[key] = value.value
        await config_facade.ModelSet(config=config)

    async def set_constraints(self, constraints):
        """Set machine constraints on this model.

        :param dict config: Mapping of model constraints
        """
        client_facade = client.ClientFacade.from_connection(self.connection())
        await client_facade.SetModelConstraints(
            application='',
            constraints=constraints)

    async def get_action_output(self, action_uuid, wait=None):
        """Get the results of an action by ID.

        :param str action_uuid: Id of the action
        :param int wait: Time in seconds to wait for action to complete.
        :return dict: Output from action
        :raises: :class:`JujuError` if invalid action_uuid
        """
        action_facade = client.ActionFacade.from_connection(
            self.connection()
        )
        entity = [{'tag': tag.action(action_uuid)}]
        # Cannot use self.wait_for_action as the action event has probably
        # already happened and self.wait_for_action works by processing
        # model deltas and checking if they match our type. If the action
        # has already occured then the delta has gone.

        async def _wait_for_action_status():
            while True:
                action_output = await action_facade.Actions(entities=entity)
                if action_output.results[0].status in ('completed', 'failed'):
                    return
                else:
                    await asyncio.sleep(1)
        await asyncio.wait_for(
            _wait_for_action_status(),
            timeout=wait)
        action_output = await action_facade.Actions(entities=entity)
        # ActionResult.output is None if the action produced no output
        if action_output.results[0].output is None:
            output = {}
        else:
            output = action_output.results[0].output
        return output

    async def get_action_status(self, uuid_or_prefix=None, name=None):
        """Get the status of all actions, filtered by ID, ID prefix, or name.

        :param str uuid_or_prefix: Filter by action uuid or prefix
        :param str name: Filter by action name

        """
        results = {}
        action_results = []
        action_facade = client.ActionFacade.from_connection(
            self.connection()
        )
        if name:
            name_results = await action_facade.FindActionsByNames(names=[name])
            action_results.extend(name_results.actions[0].actions)
        if uuid_or_prefix:
            # Collect list of actions matching uuid or prefix
            matching_actions = await action_facade.FindActionTagsByPrefix(
                prefixes=[uuid_or_prefix])
            entities = []
            for actions in matching_actions.matches.values():
                entities = [{'tag': a.tag} for a in actions]
            # Get action results matching action tags
            uuid_results = await action_facade.Actions(entities=entities)
            action_results.extend(uuid_results.results)
        for a in action_results:
            results[tag.untag('action-', a.action.tag)] = a.status
        return results

    def get_budget(self, budget_name):
        """Get budget usage info.

        :param str budget_name: Name of budget

        """
        raise NotImplementedError()

    async def get_status(self, filters=None, utc=False):
        """Return the status of the model.

        :param str filters: Optional list of applications, units, or machines
            to include, which can use wildcards ('*').
        :param bool utc: Display time as UTC in RFC3339 format

        """
        client_facade = client.ClientFacade.from_connection(self.connection())
        return await client_facade.FullStatus(patterns=filters)

    def sync_tools(
            self, all_=False, destination=None, dry_run=False, public=False,
            source=None, stream=None, version=None):
        """Copy Juju tools into this model.

        :param bool all_: Copy all versions, not just the latest
        :param str destination: Path to local destination directory
        :param bool dry_run: Don't do the actual copy
        :param bool public: Tools are for a public cloud, so generate mirrors
            information
        :param str source: Path to local source directory
        :param str stream: Simplestreams stream for which to sync metadata
        :param str version: Copy a specific major.minor version

        """
        raise NotImplementedError()

    def unblock(self, *commands):
        """Unblock an operation that would alter this model.

        :param str *commands: The commands to unblock. Valid values are
            'all-changes', 'destroy-model', 'remove-object'

        """
        raise NotImplementedError()

    def unset_config(self, *keys):
        """Unset configuration on this model.

        :param str *keys: The keys to unset

        """
        raise NotImplementedError()

    def upgrade_gui(self):
        """Upgrade the Juju GUI for this model.

        """
        raise NotImplementedError()

    def upgrade_juju(
            self, dry_run=False, reset_previous_upgrade=False,
            upload_tools=False, version=None):
        """Upgrade Juju on all machines in a model.

        :param bool dry_run: Don't do the actual upgrade
        :param bool reset_previous_upgrade: Clear the previous (incomplete)
            upgrade status
        :param bool upload_tools: Upload local version of tools
        :param str version: Upgrade to a specific version

        """
        raise NotImplementedError()

    def upload_backup(self, archive_path):
        """Store a backup archive remotely in Juju.

        :param str archive_path: Path to local archive

        """
        raise NotImplementedError()

    @property
    def charmstore(self):
        return self._charmstore

    async def get_metrics(self, *tags):
        """Retrieve metrics.

        :param str *tags: Tags of entities from which to retrieve metrics.
            No tags retrieves the metrics of all units in the model.
        :return: Dictionary of unit_name:metrics

        """
        log.debug("Retrieving metrics for %s",
                  ', '.join(tags) if tags else "all units")

        metrics_facade = client.MetricsDebugFacade.from_connection(
            self.connection())

        entities = [client.Entity(tag) for tag in tags]
        metrics_result = await metrics_facade.GetMetrics(entities=entities)

        metrics = collections.defaultdict(list)

        for entity_metrics in metrics_result.results:
            error = entity_metrics.error
            if error:
                if "is not a valid tag" in error:
                    raise ValueError(error.message)
                else:
                    raise Exception(error.message)

            for metric in entity_metrics.metrics:
                metrics[metric.unit].append(vars(metric))

        return metrics

    async def create_offer(self, endpoint, offer_name=None, application_name=None):
        """
        Offer a deployed application using a series of endpoints for use by
        consumers.

        @param endpoint: holds the application and endpoint you want to offer
        @param offer_name: over ride the offer name to help the consumer
        """
        controller = await self.get_controller()
        return await controller.create_offer(self.info.uuid, endpoint,
                                             offer_name=offer_name,
                                             application_name=application_name)

    async def list_offers(self):
        """
        Offers list information about applications' endpoints that have been
        shared and who is connected.
        """
        controller = await self.get_controller()
        return await controller.list_offers(self.info.name)

    async def remove_offer(self, endpoint, force=False):
        """
        Remove offer for an application.

        Offers will also remove relations to those offers, use force to do
        so, without an error.
        """
        controller = await self.get_controller()
        return await controller.remove_offer(self.info.uuid, endpoint, force)

    async def consume(self, endpoint, application_alias="", controller_name=None):
        """
        Adds a remote offer to the model. Relations can be created later using
        "juju relate".
        """
        try:
            offer = parse_offer_url(endpoint)
        except OfferParseError as e:
            log.error(e.message)
            raise
        if offer.has_endpoint():
            raise JujuError("remote offer {} should not include an endpoint".format(endpoint))
        if offer.user == "":
            offer.user = self.info.username
            endpoint = offer.string()

        source = await self._get_source_api(offer, controller_name=controller_name)
        consume_details = await source.get_consume_details(offer.as_local().string())
        if consume_details is None or consume_details.offer is None:
            raise JujuAPIError("missing consuming offer url for {}".format(offer.string()))

        offer_url = parse_offer_url(consume_details.offer.offer_url)
        offer_url.source = offer.source

        consume_details.offer.offer_url = offer_url.string()
        consume_details.offer.application_alias = application_alias

        arg = _create_consume_args(consume_details.offer,
                                   consume_details.macaroon,
                                   consume_details.external_controller)

        facade = client.ApplicationFacade.from_connection(self.connection())
        results = await facade.Consume(args=[arg])
        if len(results.results) != 1:
            raise JujuAPIError("expected 1 result, recieved {}".format(len(results.results)))
        if results.results[0].error is not None:
            raise JujuAPIError(results.results[0].error)
        local_name = offer_url.application
        if application_alias != "":
            local_name = application_alias
        return local_name

    async def remove_saas(self, name):
        """
        Removing a consumed (SAAS) application will terminate any relations that
        application has, potentially leaving any related local applications
        in a non-functional state.
        """
        if not is_valid_application(name):
            raise JujuError("invalid SAAS application name {}".format(name))

        arg = client.DestroyConsumedApplicationParams()
        arg.application_tag = application_tag(name)

        facade = client.ApplicationFacade.from_connection(self.connection())
        return await facade.DestroyConsumedApplications(applications=[arg])

    async def export_bundle(self, filename=None):
        """
        Exports the current model configuration as a reusable bundle.
        """
        facade = client.BundleFacade.from_connection(self.connection())
        result = await facade.ExportBundle()
        if result.error is not None:
            raise JujuAPIError(result.error)

        if filename is None:
            return result.result

        try:
            with open(filename, "w") as file:
                file.write(result.result)
        except IOError:
            raise

    async def _get_source_api(self, url, controller_name=None):
        controller = Controller()
        if url.has_empty_source():
            current = await self.get_controller()
            if current.controller_name is not None:
                controller_name = current.controller_name
        await controller.connect(controller_name=controller_name)
        return controller


def _create_consume_args(offer, macaroon, controller_info):
    """
    Convert a typed object that has been normalised to a overrided typed
    definition.

    @param offer: takes an offer and serialises it into a valid type
    @param macaroon: takes a macaroon and serialises it into a valid type
    @param controller_info: takes a controller information and serialises it into
    a valid type.
    """
    endpoints = []
    for ep in offer.endpoints:
        endpoints.append(client.RemoteEndpoint(interface=ep.interface,
                                               limit=ep.limit,
                                               name=ep.name,
                                               role=ep.role))
    users = []
    for u in offer.users:
        users.append(client.OfferUserDetails(access=u.access,
                                             display_name=u.display_name,
                                             user=u.user))
    external_controller = client.ExternalControllerInfo(addrs=controller_info.addrs,
                                                        ca_cert=controller_info.ca_cert,
                                                        controller_alias=controller_info.controller_alias,
                                                        controller_tag=controller_info.controller_tag)
    caveats = []
    for c in macaroon.unknown_fields["caveats"]:
        caveats.append(Caveat(cid=c["cid"]))
    macaroon = Macaroon(signature=macaroon.unknown_fields["signature"],
                        caveats=caveats,
                        location=macaroon.unknown_fields["location"],
                        identifier=macaroon.unknown_fields["identifier"])

    arg = client.ConsumeApplicationArg()
    arg.application_description = offer.application_description
    arg.endpoints = endpoints
    arg.offer_name = offer.offer_name
    arg.offer_url = offer.offer_url
    arg.offer_uuid = offer.offer_uuid
    arg.source_model_tag = offer.source_model_tag
    arg.users = users
    arg.application_alias = offer.application_alias
    arg.external_controller = external_controller
    arg.macaroon = macaroon

    return arg


class CharmStore:
    """
    Async wrapper around theblues.charmstore.CharmStore
    """
    def __init__(self, loop, cs_timeout=20):
        self.loop = loop
        self._cs = theblues.charmstore.CharmStore(timeout=cs_timeout)

    def __getattr__(self, name):
        """
        Wrap method calls in coroutines that use run_in_executor to make them
        async.
        """
        attr = getattr(self._cs, name)
        if not callable(attr):
            wrapper = partial(getattr, self._cs, name)
            setattr(self, name, wrapper)
        else:
            async def coro(*args, **kwargs):
                method = partial(attr, *args, **kwargs)
                for attempt in range(1, 4):
                    try:
                        return await self.loop.run_in_executor(None, method)
                    except theblues.errors.ServerError:
                        if attempt == 3:
                            raise
                        await asyncio.sleep(1, loop=self.loop)
            setattr(self, name, coro)
            wrapper = coro
        return wrapper


class CharmArchiveGenerator:
    """
    Create a Zip archive of a local charm directory for upload to a controller.

    This is used automatically by
    `Model.add_local_charm_dir <#juju.model.Model.add_local_charm_dir>`_.
    """
    def __init__(self, path):
        self.path = os.path.abspath(os.path.expanduser(path))

    def make_archive(self, path):
        """Create archive of directory and write to ``path``.

        :param path: Path to archive

        Ignored::

            * build/* - This is used for packing the charm itself and any
                          similar tasks.
            * */.*    - Hidden files are all ignored for now.  This will most
                          likely be changed into a specific ignore list
                          (.bzr, etc)

        """
        zf = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
        for dirpath, dirnames, filenames in os.walk(self.path):
            relative_path = dirpath[len(self.path) + 1:]
            if relative_path and not self._ignore(relative_path):
                zf.write(dirpath, relative_path)
            for dirname in dirnames:
                archive_name = os.path.join(relative_path, dirname)
                real_path = os.path.join(dirpath, dirname)
                if os.path.islink(real_path):
                    self._check_link(real_path)
                    self._write_symlink(zf, os.readlink(real_path), archive_name)
            for name in filenames:
                archive_name = os.path.join(relative_path, name)
                if not self._ignore(archive_name):
                    real_path = os.path.join(dirpath, name)
                    self._check_type(real_path)
                    if os.path.islink(real_path):
                        self._check_link(real_path)
                        self._write_symlink(
                            zf, os.readlink(real_path), archive_name)
                    else:
                        zf.write(real_path, archive_name)
        zf.close()
        return path

    def _check_type(self, path):
        """Check the path
        """
        s = os.stat(path)
        if stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode):
            return path
        raise ValueError("Invalid Charm at %s %s" % (
            path, "Invalid file type for a charm"))

    def _check_link(self, path):
        link_path = os.readlink(path)
        if link_path[0] == "/":
            raise ValueError(
                "Invalid Charm at %s: %s" % (
                    path, "Absolute links are invalid"))
        path_dir = os.path.dirname(path)
        link_path = os.path.join(path_dir, link_path)
        if not link_path.startswith(os.path.abspath(self.path)):
            raise ValueError(
                "Invalid charm at %s %s" % (
                    path, "Only internal symlinks are allowed"))

    def _write_symlink(self, zf, link_target, link_path):
        """Package symlinks with appropriate zipfile metadata."""
        info = zipfile.ZipInfo()
        info.filename = link_path
        info.create_system = 3
        # Magic code for symlinks / py2/3 compat
        # 27166663808 = (stat.S_IFLNK | 0755) << 16
        info.external_attr = 2716663808
        zf.writestr(info, link_target)

    def _ignore(self, path):
        if path == "build" or path.startswith("build/"):
            return True
        if path.startswith('.'):
            return True


class ModelInfo(ModelEntity):
    @property
    def tag(self):
        return tag.model(self.uuid)
