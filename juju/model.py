# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import base64
import collections
import hashlib
import json
import logging
import os
import sys
import re
import stat
import tempfile
import warnings
import weakref
import zipfile
from concurrent.futures import CancelledError
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path

import yaml
import websockets

from . import provisioner, tag, utils, jasyncio
from .annotationhelper import _get_annotations, _set_annotations
from .bundle import BundleHandler, get_charm_series, is_local_charm
from .charmhub import CharmHub
from .client import client, connector
from .client.overrides import Caveat, Macaroon
from .constraints import parse as parse_constraints
from .controller import Controller, ConnectedController
from .delta import get_entity_class, get_entity_delta
from .errors import JujuAPIError, JujuError, JujuModelConfigError, JujuBackupError
from .errors import JujuModelError, JujuAppError, JujuUnitError, JujuAgentError, JujuMachineError, PylibjujuError, JujuNotSupportedError
from .exceptions import DeadEntityException
from .names import is_valid_application
from .offerendpoints import ParseError as OfferParseError
from .offerendpoints import parse_local_endpoint, parse_offer_url
from .origin import Channel, Source
from .placement import parse as parse_placement
from .secrets import create_secret_data, read_secret_data
from .tag import application as application_tag
from .url import URL, Schema
from .version import DEFAULT_ARCHITECTURE

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
    def subordinate_units(self):
        """Return a map of unit-id:Unit for all subordinate units"""
        return {u_name: u for u_name, u in self.units.items() if u.is_subordinate}

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
        self._status = 'unknown'

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
        # Allow the overriding of entity names from the type instead of from
        # the class name. Useful because Model and ModelInfo clash and we really
        # want ModelInfo to be called Model.
        if hasattr(self.__class__, "type_name_override") and callable(self.__class__.type_name_override):
            return self.__class__.type_name_override()

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


class DeployTypeResult:
    """DeployTypeResult represents the result of a deployment type after a
    resolution.
    """

    def __init__(self, identifier, origin, app_name, is_local=False, is_bundle=False):
        self.identifier = identifier
        self.origin = origin
        self.app_name = app_name
        self.is_local = is_local
        self.is_bundle = is_bundle


class LocalDeployType:
    """LocalDeployType deals with local only deployments.
    """

    async def resolve(self, charm_path, architecture,
                      app_name=None, channel=None, series=None,
                      revision=None, entity_url=None, force=False,
                      model_conf=None):
        """resolve attempts to resolve a local charm or bundle using the url
        and architecture. If information is missing, it will attempt to backfill
        that information, before sending the result back.

        -- revision flag is ignored for local charms
        """

        entity_path = Path(charm_path)
        if entity_path.suffix == '.yaml':
            bundle_path = entity_path
        else:
            bundle_path = entity_path / 'bundle.yaml'

        origin = client.CharmOrigin(source="local", architecture=architecture)
        if not (entity_path.is_dir() or entity_path.is_file()):
            raise JujuError('{} path not found'.format(entity_url))

        is_bundle = bundle_path.exists()

        if app_name is None:
            if is_bundle:
                bundle_with_overlays = [b for b in yaml.safe_load_all(bundle_path.read_text())]
                app_name = bundle_with_overlays[0].get('name', '')
            else:
                app_name = utils.get_local_charm_metadata(entity_path)["name"]

        return DeployTypeResult(
            identifier=charm_path,
            origin=origin,
            app_name=app_name,
            is_local=True,
            is_bundle=is_bundle,
        )


class CharmhubDeployType:
    """CharmhubDeployType defines a class for resolving and deploying charmhub
    charms and bundles.
    """

    def __init__(self, charm_resolver):
        self.charm_resolver = charm_resolver

    async def resolve(self, url, architecture,
                      app_name=None, channel=None, series=None,
                      revision=None, entity_url=None, force=False,
                      model_conf=None):
        """resolve attempts to resolve charmhub charms or bundles. A request to
        the charmhub API is required to correctly determine the charm url and
        underlying origin.
        """
        if revision and not channel:
            raise JujuError('specifying a revision requires a channel for future upgrades. Please use --channel')

        ch = Channel('latest', 'stable')
        if channel is not None:
            ch = Channel.parse(channel).normalize()

        base = client.Base()
        if series:
            base.channel = ch.normalize().compute_base_channel(series=series)
            base.name = 'ubuntu'

        origin = client.CharmOrigin(source=Source.CHARM_HUB.value,
                                    architecture=architecture,
                                    risk=ch.risk,
                                    track=ch.track,
                                    base=base,
                                    revision=revision,
                                    )

        charm_url, origin = await self.charm_resolver(url, origin, force, series, model_conf)

        is_bundle = origin.type_ == "bundle"
        if is_bundle and revision and channel:
            raise JujuError('revision and channel are mutually exclusive when deploying a bundle. Please choose one.')

        if app_name is None:
            app_name = charm_url.name

        return DeployTypeResult(
            identifier=str(charm_url),
            app_name=app_name,
            origin=origin,
            is_bundle=is_bundle,
        )


class Model:
    """
    The main API for interacting with a Juju model.
    """
    def __init__(
        self,
        max_frame_size=None,
        bakery_client=None,
        jujudata=None,
    ):
        """Instantiate a new Model.

        The connect method will need to be called before this
        object can be used for anything interesting.

        If jujudata is None, jujudata.FileJujuData will be used.

        :param max_frame_size: See
            `juju.client.connection.Connection.MAX_FRAME_SIZE`
        :param bakery_client httpbakery.Client: The bakery client to use
            for macaroon authorization.
        :param jujudata JujuData: The source for current controller information
        """
        self._connector = connector.Connector(
            max_frame_size=max_frame_size,
            bakery_client=bakery_client,
            jujudata=jujudata,
        )
        self._observers = weakref.WeakValueDictionary()
        self.state = ModelState(self)
        self._info = None
        self._mode = None
        self._watch_stopping = jasyncio.Event()
        self._watch_stopped = jasyncio.Event()
        self._watch_received = jasyncio.Event()
        self._watch_stopped.set()

        self._charmhub = CharmHub(self)

        self.deploy_types = {
            Schema.LOCAL: LocalDeployType(),
            Schema.CHARM_HUB: CharmhubDeployType(self._resolve_charm),
        }

    def is_connected(self):
        """Reports whether the Model is currently connected."""
        return self._connector.is_connected()

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
        :param int max_frame_size: The maximum websocket frame size to allow.
        :param specified_facades: Overwrite the facades with a series of
            specified facades.
        """
        is_debug_log_conn = 'debug_log_conn' in kwargs
        if not is_debug_log_conn:
            await self.disconnect()
        model_name = model_uuid = None
        if 'endpoint' not in kwargs and len(args) < 2:
            # Then we're using the model_name to pick the model
            if args and 'model_name' in kwargs:
                raise TypeError('connect() got multiple values for model_name')
            elif args:
                model_name = args[0]
            else:
                model_name = kwargs.pop('model_name', None)
            model_uuid = await self._connector.connect_model(model_name, **kwargs)
        else:
            # Then we're using the endpoint to pick the model
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
                'max_frame_size',
            ]
            for i, arg in enumerate(args):
                kwargs[arg_names[i]] = arg
            model_uuid = kwargs['uuid']
            if not {'endpoint', 'uuid'}.issubset(kwargs):
                raise ValueError('endpoint and uuid are required '
                                 'if model_name not given')
            if not ({'username', 'password'}.issubset(kwargs) or
                    {'bakery_client', 'macaroons'}.intersection(kwargs)):
                raise ValueError('Authentication parameters are required '
                                 'if model_name not given')
            await self._connector.connect(**kwargs)
        if not is_debug_log_conn:
            await self._after_connect(model_name, model_uuid)

    async def connect_model(self, model_name, **kwargs):
        """
        .. deprecated:: 0.6.2
           Use ``connect(model_name=model_name)`` instead.
        """
        return await self.connect(model_name=model_name, **kwargs)

    async def connect_current(self):
        """
        .. deprecated:: 0.6.2
           Use ``connect()`` instead.
        """
        return await self.connect()

    async def connect_to(self, connection):
        conn_params = connection.connect_params()
        await self._connect_direct(**conn_params)

    async def _connect_direct(self, **kwargs):
        if self.info:
            uuid = self.info.uuid
        elif 'uuid' in kwargs:
            uuid = kwargs['uuid']
        else:
            raise PylibjujuError("Unable to find uuid for the model")
        await self.disconnect()
        await self._connector.connect(**kwargs)
        await self._after_connect(model_uuid=uuid)

    async def _after_connect(self, model_name=None, model_uuid=None):
        self._watch()

        # Wait for the first packet of data from the AllWatcher,
        # which contains all information on the model.
        # TODO this means that we can't do anything until
        # we've received all the model data, which might be
        # a whole load of unneeded data if all the client wants
        # to do is make one RPC call.
        async def watch_received_waiter():
            await self._watch_received.wait()
        waiter = jasyncio.create_task(watch_received_waiter())

        # If we just wait for the _watch_received event and the _all_watcher task
        # fails (e.g. because API fails like migration is in progress), then
        # we'll hang because the _watch_received will never be set
        # Instead, we watch for two things, 1) _watch_received, 2) _all_watcher done
        # If _all_watcher is done before the _watch_received, then we should see
        # (and raise) an exception coming from the _all_watcher
        # Otherwise (i.e. _watch_received is set), then we're good to go
        done, pending = await jasyncio.wait([waiter, self._watcher_task],
                                            return_when=jasyncio.FIRST_COMPLETED)
        if self._watcher_task in done:
            # Cancel the _watch_received.wait
            waiter.cancel()
            # If there's no exception, then why did the _all_watcher broke its loop?
            if not self._watcher_task.exception():
                raise JujuError("AllWatcher task is finished abruptly without an exception.")
            raise self._watcher_task.exception()

        if self._info is None:
            # TODO (cderici): See if this can be optimized away, or at least
            # be done lazily (i.e. not everytime after_connect, but whenever
            # self.info is needed -- which here can be bypassed if model_uuid
            # is known)
            async with ConnectedController(self.connection()) as contr:
                self._info = await contr.get_model_info(model_name, model_uuid)
                log.debug('Got ModelInfo: %s', vars(self.info))

        self.uuid = self.info.uuid

    async def disconnect(self):
        """Shut down the watcher task and close websockets.

        """
        if not self._watch_stopped.is_set():
            log.debug('Stopping watcher task')
            self._watch_stopping.set()
            # If the _all_watcher task is finished,
            # check to see an exception, if yes, raise,
            # otherwise we should see the _watch_stopped
            # flag is set
            if self._watcher_task.done() and self._watcher_task.exception():
                raise self._watcher_task.exception()
            await self._watch_stopped.wait()
            self._watch_stopping.clear()

        if self.is_connected():
            await self._connector.disconnect(entity='model')
            self._info = None

    async def add_local_charm_dir(self, charm_dir, series):
        """Upload a local charm to the model.

        This will automatically generate an archive from
        the charm dir.

        :param charm_dir: Path to the charm directory
        :param series: Charm series

        """
        charm_dir = Path(charm_dir)
        if charm_dir.suffix == '.charm':
            fn = charm_dir
        else:
            fn = tempfile.NamedTemporaryFile().name
            CharmArchiveGenerator(str(charm_dir)).make_archive(fn)
        with open(str(fn), 'rb') as fh:
            func = partial(
                self.add_local_charm, fh, series, os.stat(str(fn)).st_size)
            loop = jasyncio.get_running_loop()
            charm_url = await loop.run_in_executor(None, func)

        log.debug('Uploaded local charm: %s -> %s', charm_dir, charm_url)
        return charm_url

    def add_local_charm(self, charm_file, series="", size=None):
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
        await self.block_until(
            lambda: len(self.applications) == 0
        )
        for machine in self.machines.values():
            await machine.destroy(force=force)
        await self.block_until(
            lambda: len(self.machines) == 0
        )

    async def create_storage_pool(self, name, provider_type, attributes=""):
        """Create or define a storage pool.

        :param str name: a pool name
        :param str provider_type: provider type (defaults to "kubernetes" for
        Kubernetes models)
        :param str attributes: attributes for configuration as space-separated pairs,
        e.g. tags, size, path, etc.
        :return:
        """
        _attrs = [splt.split("=") for splt in attributes.split()]

        storage_facade = client.StorageFacade.from_connection(self.connection())
        return await storage_facade.CreatePool(pools=[client.StoragePool(
            name=name,
            provider=provider_type,
            attrs=dict(_attrs)
        )])

    async def remove_storage_pool(self, name):
        """Remove an existing storage pool.

        :param str name:
        :return:
        """
        storage_facade = client.StorageFacade.from_connection(self.connection())
        return await storage_facade.RemovePool(pools=[client.StoragePoolDeleteArg(name)])

    async def update_storage_pool(self, name, attributes=""):
        """ Update storage pool attributes.

        :param name:
        :param attributes: "key=value key=value ..."
        :return:
        """
        _attrs = dict([splt.split("=") for splt in attributes.split()])
        if len(_attrs) == 0:
            raise JujuError("Expected at least one attribute to update")

        storage_facade = client.StorageFacade.from_connection(self.connection())
        return await storage_facade.UpdatePool(pools=[client.StoragePool(
            name=name,
            attrs=_attrs,
        )])

    async def list_storage(self, filesystem=False, volume=False):
        """Lists storage details.

        :param bool filesystem: List filesystem storage
        :param bool volume: List volume storage
        :return:
        """
        storage_facade = client.StorageFacade.from_connection(self.connection())

        if filesystem and volume:
            raise JujuError("--filesystem and --volume can not be used together")
        if filesystem:
            _res = await storage_facade.ListFilesystems(filters=[client.FilesystemFilter()])
        elif volume:
            _res = await storage_facade.ListVolumes(filters=[client.VolumeFilter()])
        else:
            _res = await storage_facade.ListStorageDetails(filters=[client.StorageFilter()])

        err = _res.results[0].error
        res = _res.results[0].result

        if err is not None:
            raise JujuError(err.message)

        return [details.serialize() for details in res]

    async def show_storage_details(self, *storage_ids):
        """Shows storage instance information.

        :param []str storage_ids:
        :return:
        """
        if not storage_ids:
            raise JujuError("Expected at least one storage ID")

        storage_facade = client.StorageFacade.from_connection(self.connection())
        res = await storage_facade.StorageDetails(entities=[client.Entity(tag.storage(s)) for s in storage_ids])
        return [s.result.serialize() for s in res.results]

    async def list_storage_pools(self):
        """List storage pools.

        :return:
        """
        # TODO (cderici): Filter on pool type, name.
        storage_facade = client.StorageFacade.from_connection(self.connection())
        res = await storage_facade.ListPools(filters=[client.StoragePoolFilter()])
        err = res.results[0].error
        if err:
            raise JujuError(err.message)
        return [p.serialize() for p in res.results[0].storage_pools]

    async def remove_storage(self, *storage_ids, force=False, destroy_storage=False):
        """Removes storage from the model.

        :param bool force: Remove storage even if it is currently attached
        :param bool destroy_storage: Remove the storage and destroy it
        :param []str storage_ids:
        :return:
        """
        if not storage_ids:
            raise JujuError("Expected at least one storage ID")

        storage_facade = client.StorageFacade.from_connection(self.connection())
        ret = await storage_facade.Remove(storage=[client.RemoveStorageInstance(
            destroy_storage=destroy_storage,
            force=force,
            tag=s,
        ) for s in storage_ids])
        if ret.results[0].error:
            raise JujuError(ret.results[0].error.message)

    async def remove_application(self, app_name, block_until_done=False, force=False, destroy_storage=False, no_wait=False):
        """Removes the given application from the model.

        :param str app_name: Name of the application
        :param bool force: Completely remove an application and all its dependencies. (=false)
        :param bool destroy_storage: Destroy storage attached to application unit. (=false)
        :param bool no_wait: Rush through application removal without waiting for each individual step to complete (=false)
        :param bool block_until_done: Ensure the app is removed from the
        model when returned
        """
        if app_name not in self.applications:
            raise JujuError("Given application doesn't seem to appear in the\
             model: %s\nCurrent applications are: %s" %
                            (app_name, self.applications))
        await self.applications[app_name].remove(destroy_storage=destroy_storage,
                                                 force=force,
                                                 no_wait=no_wait,
                                                 )
        if block_until_done:
            await self.block_until(lambda: app_name not in self.applications)

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
                                wait_period=wait_period)
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
    def subordinate_units(self):
        """Return a map of unit-id:Unit for all subordiante units currently in
        the model.

        """
        return self.state.subordinate_units

    @property
    def relations(self):
        """Return a list of all Relations currently in the model.

        """
        return list(self.state.relations.values())

    @property
    def charmhub(self):
        """Return a charmhub repository for requesting charm information using
        the charm-hub-url model config.

        """
        return self._charmhub

    @property
    def name(self):
        """Return the name of this model

        """
        if self._info is None:
            raise JujuModelError("Model is not connected")
        return self._info.name

    @property
    def info(self):
        """Return the cached client.ModelInfo object for this Model.

        If Model.get_info() has not been called, this will return None.
        """
        return self._info

    @property
    def strict_mode(self):
        return self._mode is not None and "strict" in self._mode

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

        def _post_step(obj):
            # Once we get the model, ensure we're running in the correct state
            # as a post step.
            if isinstance(obj, ModelInfo) and obj.safe_data is not None:
                model_config = obj.safe_data["config"]
                if "mode" in model_config:
                    self._mode = model_config["mode"]

        async def _all_watcher():
            # First attempt to get the model config so we know what mode the
            # library should be running in.
            model_config = await self.get_config()
            if "mode" in model_config:
                self._mode = model_config["mode"]["value"]

            try:
                allwatcher = client.AllWatcherFacade.from_connection(
                    self.connection())
                while not self._watch_stopping.is_set():
                    try:
                        results = await utils.run_with_interrupt(
                            allwatcher.Next(),
                            self._watch_stopping)
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
                        entity = None
                        try:
                            entity = get_entity_delta(delta)
                        except KeyError:
                            if self.strict_mode:
                                raise JujuError("unknown delta type '{}'".format(delta.entity))

                        if not self.strict_mode and entity is None:
                            continue
                        old_obj, new_obj = self.state.apply_delta(entity)
                        await self._notify_observers(entity, old_obj, new_obj)
                        # Post step ensure that we can handle any settings
                        # that need to be correctly set as a post step.
                        _post_step(new_obj)
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
        self._watcher_task = jasyncio.create_task(_all_watcher())

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
                jasyncio.ensure_future(o(delta, old_obj, new_obj, self))

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
        q = jasyncio.Queue()

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
        client_facade = client.MachineManagerFacade.from_connection(self.connection())
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
        """
        .. deprecated:: 2.9.9
           Use ``relate()`` instead
        """
        return await self.relate(relation1, relation2)

    async def integrate(self, relation1, relation2):
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
                async with ConnectedController(self.connection()) as current:
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

    async def relate(self, relation1, relation2):
        """The relate function is deprecated in favor of integrate.

        The logic is the same.
        """
        log.warning("relate is deprecated and will be removed. Use integrate instead.")
        return await self.integrate(relation1, relation2)

    async def add_space(self, name, cidrs=None, public=True):
        """Add a new network space.

        Adds a new space with the given name and associates the given
        (optional) list of existing subnet CIDRs with it.

        :param str name: Name of the space
        :param List[str] cidrs: Optional list of existing subnet CIDRs
        """
        space_facade = client.SpacesFacade.from_connection(self.connection())
        spaces = [
            {
                "cidrs": cidrs,
                "space-tag": tag.space(name),
                "public": public}]
        return await space_facade.CreateSpaces(spaces=spaces)

    async def add_ssh_key(self, user, key):
        """Add a public SSH key to this model.

        :param str user: The username of the user
        :param str key: The public ssh key

        """
        key_facade = client.KeyManagerFacade.from_connection(self.connection())
        return await key_facade.AddKeys(ssh_keys=[key], user=user)
    add_ssh_keys = add_ssh_key

    async def get_backups(self):
        """Retrieve metadata for backups in this model.

        :return [dict]: List of metadata for the stored backups
        """
        backups_facade = client.BackupsFacade.from_connection(self.connection())
        _backups_metadata = await backups_facade.List()
        backups_metadata = _backups_metadata.serialize()
        if 'list' not in backups_metadata:
            raise JujuAPIError("Unexpected response metadata : %s" % backups_metadata)
        return backups_metadata['list']

    async def create_backup(self, notes=None):
        """Create a backup of this model.

        :param str note: A note to store with the backup
        :param bool keep_copy: Keep a copy of the archive on the controller
        :param bool no_download: Do not download the backup archive
        :return str, dict: Filename for the downloaded archive file, Extra metadata for the created backup

        """
        backups_facade = client.BackupsFacade.from_connection(self.connection())
        results = await backups_facade.Create(notes=notes)

        if results is None:
            raise JujuAPIError("unable to create a backup")

        backup_metadata = results.serialize()

        if 'error' in backup_metadata:
            raise JujuBackupError("unable to create a backup, got %s from Juju API" % backup_metadata)

        backup_id = backup_metadata['filename']

        file_name = self.download_backup(backup_id)

        return file_name, backup_metadata

    async def debug_log(
            self, target=sys.stdout, no_tail=False, exclude_module=[],
            include_module=[], include=[], level="", limit=sys.maxsize,
            lines=10, exclude=[]):
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
        :param list exclude: Do not show log messages for these entities

        """
        if not self.is_connected():
            await self.connect()

        params = {
            'no_tail': no_tail,
            'exclude_module': exclude_module,
            'include_module': include_module,
            'include': include,
            'level': level,
            'limit': limit,
            'lines': lines,
            'exclude': exclude,
        }
        await self.connect(debug_log_conn=target, debug_log_params=params)

    async def deploy(
            self, entity_url, application_name=None, bind=None,
            channel=None, config=None, constraints=None, force=False,
            num_units=1, overlays=[], base=None, resources=None, series=None, revision=None,
            storage=None, to=None, devices=None, trust=False, attach_storage=[]):
        """Deploy a new service or bundle.

        :param str entity_url: Charm or bundle to deploy. Charm url or file path
        :param str application_name: Name to give the service
        :param dict bind: <charm endpoint>:<network space> pairs
        :param str channel: Charm store channel from which to retrieve
            the charm or bundle, e.g. 'edge'
        :param dict config: Charm configuration dictionary
        :param constraints: Service constraints
        :type constraints: :class:`juju.Constraints`
        :param bool force: Allow charm to be deployed to a machine running
            an unsupported series
        :param int num_units: Number of units to deploy
        :param [] overlays: Bundles to overlay on the primary bundle, applied in order
        :param str base: The base on which to deploy
        :param dict resources: <resource name>:<file path> pairs
        :param str series: Series on which to deploy DEPRECATED: use --base (with Juju 3.1)
        :param int revision: specifying a revision requires a channel for future upgrades for charms.
            For bundles, revision and channel are mutually exclusive.
        :param dict storage: Storage constraints TODO how do these look?
        :param to: Placement directive as a string. For example:

            '23' - place on machine 23
            'lxd:7' - place in new lxd container on machine 7
            '24/lxd/3' - place in container 3 on machine 24

            If None, a new machine is provisioned.
        :param devices: charm device constraints
        :param bool trust: Trust signifies that the charm should be deployed
            with access to trusted credentials. Hooks run by the charm can access
            cloud credentials and other trusted access credentials.

        :param str[] attach_storage: Existing storage to attach to the deployed unit
            (not available on k8s models)
        """

        if storage:
            storage = {
                k: client.Constraints(**v)
                for k, v in storage.items()
            }
        if trust and (self.info.agent_version < client.Number.from_json('2.4.0')):
            raise NotImplementedError("trusted is not supported on model version {}".format(self.info.agent_version))

        if not all([isinstance(st, str) for st in attach_storage]):
            raise JujuError("Expected attach_storage to be a list of strings, given {}".format(attach_storage))

        # Ensure what we pass in, is a string.
        entity = str(entity_url)
        if is_local_charm(entity):
            if entity.startswith("local:"):
                entity = entity[6:]
            architecture = await self._resolve_architecture()
            schema = Schema.LOCAL

        else:
            if client.CharmsFacade.best_facade_version(self.connection()) < 3:
                url = URL.parse(entity, default_store=Schema.CHARM_STORE)
            else:
                url = URL.parse(entity)
            entity = str(url)

            architecture = await self._resolve_architecture(url)
            schema = url.schema
            name = url.name

        if schema not in self.deploy_types:
            raise JujuError("unknown deploy type {}, expected charmhub or local".format(schema))

        model_conf = await self.get_config()
        res = await self.deploy_types[schema].resolve(entity, architecture,
                                                      application_name, channel,
                                                      series, revision,
                                                      entity_url, force,
                                                      model_conf)

        if res.identifier is None:
            raise JujuError('unknown charm or bundle {}'.format(entity_url))
        identifier = res.identifier

        charm_series = series
        charm_origin = res.origin
        if base:
            charm_origin.base = utils.parse_base_arg(base)

        server_side_deploy = False

        if res.is_bundle:
            handler = BundleHandler(self, trusted=trust, forced=force)
            await handler.fetch_plan(entity, charm_origin, overlays=overlays)
            await handler.execute_plan()
            extant_apps = {app for app in self.applications}
            pending_apps = handler.applications - extant_apps
            if pending_apps:
                # new apps will usually be in the model by now, but if some
                # haven't made it yet we'll need to wait on them to be added
                await jasyncio.gather(*[
                    jasyncio.ensure_future(
                        self._wait_for_new('application', app_name))
                    for app_name in pending_apps
                ])
            return [app for name, app in self.applications.items()
                    if name in handler.applications]
        else:
            if overlays:
                raise JujuError("options provided but not supported when deploying a charm: overlays=%s" % overlays)
            # XXX: we're dropping local resources here, but we don't
            # actually support them yet anyway
            if not res.is_local:
                add_charm_res = await self._add_charm(identifier, charm_origin)
                if isinstance(add_charm_res, dict):
                    # This is for backwards compatibility for older
                    # versions where AddCharm returns a dictionary
                    charm_origin = add_charm_res.get('charm_origin',
                                                     charm_origin)
                else:
                    charm_origin = add_charm_res.charm_origin
                if Schema.CHARM_HUB.matches(schema):
                    if client.ApplicationFacade.best_facade_version(self.connection()) >= 19:
                        server_side_deploy = True
                    else:
                        # TODO (cderici): this is an awkward workaround for basically not calling
                        # the AddPendingResources in case this is a server side deploy.
                        # If that's the case, then the store resources (and revisioned local
                        # resources) are handled at the server side if this is a server side deploy
                        # (local uploads are handled right after we get the pendingIDs returned
                        # from the facade call).
                        resources = await self._add_charmhub_resources(res.app_name,
                                                                       identifier,
                                                                       add_charm_res.charm_origin)

                    is_sub = await self.charmhub.is_subordinate(name)
                    if is_sub:
                        if num_units > 1:
                            raise JujuError("cannot use num_units with subordinate application")
                        num_units = 0

            else:
                # We have a local charm dir that needs to be uploaded
                charm_dir = os.path.abspath(os.path.expanduser(identifier))
                metadata = utils.get_local_charm_metadata(charm_dir)
                charm_series = charm_series or await get_charm_series(metadata, self)

                base = utils.get_local_charm_base(charm_series, charm_dir, client.Base)
                charm_origin.base = base

                if not application_name:
                    application_name = metadata['name']
                if not application_name:
                    application_name = metadata['name']
                if base is None and charm_series is None:
                    raise JujuError(
                        "Either series or base is needed to deploy the "
                        "charm at {}. ".format(charm_dir))

                identifier = await self.add_local_charm_dir(charm_dir,
                                                            charm_series)
                resources = await self.add_local_resources(application_name,
                                                           identifier,
                                                           metadata,
                                                           resources=resources)

            if config is None:
                config = {}
            if trust:
                config["trust"] = True

            return await self._deploy(
                charm_url=identifier,
                application=res.app_name,
                series=charm_series,
                config=config,
                constraints=constraints,
                endpoint_bindings=bind,
                resources=resources,
                storage=storage,
                channel=channel,
                num_units=num_units,
                placement=parse_placement(to),
                devices=devices,
                charm_origin=charm_origin,
                attach_storage=attach_storage,
                force=force,
                server_side_deploy=server_side_deploy,
            )

    async def _add_charm(self, charm_url, origin):
        """_add_charm sends the given origin and the url to the Juju API too add the charm to the
        state. Either calls the CharmsFacade.AddCharm for (> version 2), or the
        ClientFacade.AddCharm (for older versions).

        :param str charm_url: the url of the charm to be added
        :param client.CharmOrigin origin: the origin for the charm to be added

        :returns client.CharmOriginResult
        """
        # client facade is deprecated with in Juju, and smaller, more focused
        # facades have been created and we'll use that if it's available.
        charms_cls = client.CharmsFacade
        if charms_cls.best_facade_version(self.connection()) > 2:
            charms_facade = charms_cls.from_connection(self.connection())
            return await charms_facade.AddCharm(charm_origin=origin, url=charm_url, force=False)

        client_facade = client.ClientFacade.from_connection(self.connection())
        return await client_facade.AddCharm(channel=str(origin.risk), url=charm_url, force=False)

    async def _resolve_charm(self, url, origin, force=False, series=None, model_config=None):
        """Calls Charms.ResolveCharms to resolve all the fields of the
        charm_origin and also the url and the supported_series

        :param str url: The url of the charm
        :param client.CharmOrigin origin: The manually constructed origin
        based on what we know about the charm and the deployment so far

        Returns the confirmed origin returned by the Juju API to be used in
        calls like ApplicationFacade.Deploy

        :returns url.URL, client.CharmOrigin, [str]
        """
        charms_cls = client.CharmsFacade
        if charms_cls.best_facade_version(self.connection()) < 3:
            raise JujuError("resolve charm")

        charms_facade = charms_cls.from_connection(self.connection())

        # TODO (cderici): following part can be refactored out, since the
        #  origin should be set (including the base) before calling this,
        #  though all tests need to run (in earlier versions too) before
        #  committing to make sure there's no regression
        source = Source.CHARM_HUB.value

        resolve_origin = {'source': source, 'architecture': origin.architecture,
                          'track': origin.track, 'risk': origin.risk,
                          'base': origin.base, 'revision': origin.revision,
                          }

        resp = await charms_facade.ResolveCharms(resolve=[{
            'reference': str(url),
            'charm-origin': resolve_origin
        }])
        if len(resp.results) != 1:
            raise JujuError("expected one result, received {}".format(resp.results))

        result = resp.results[0]
        if result.error:
            raise JujuError(f'resolving {url} : {result.error.message}')

        # TODO (cderici) : supported_bases
        supported_series = result.get('supported_series', result.unknown_fields['supported-series'])
        resolved_origin = result.charm_origin
        charm_url = URL.parse(result.url)

        # run the series selector to get a series for the base
        selected_series = utils.series_selector(series, charm_url, model_config, supported_series, force)
        result.charm_origin.base = utils.get_base_from_origin_or_channel(resolved_origin, selected_series)
        charm_url.series = selected_series

        return charm_url, resolved_origin

    async def _resolve_architecture(self, url=None):
        """_resolve_architecture returns the architecture for a given charm url.
        If the charm url is absent, or doesn't specific an arch, we return the
        default architecture from the model.

        :param str url: the client.URL to determine the arch for

        :returns str architecture for the given url
        """
        if url is not None and url.architecture:
            return url.architecture

        constraints = await self.get_constraints()
        if 'arch' in constraints:
            return constraints['arch']

        return DEFAULT_ARCHITECTURE

    async def _add_charmhub_resources(self, application,
                                      entity_url,
                                      origin,
                                      overrides=None):
        """_add_charmhub_resources is called by the deploy to add pending resources requested by
        the charm being deployed. It calls the ResourcesFacade.AddPendingResources.

        :param str application: the name of the application
        :param client.CharmURL entity_url: url for the charm that we add resources for
        :param client.CharmOrigin origin: origin for the charm that we add resources for

        :returns [string]string resource_map that is a map of resources to their assigned
        pendingIDs.
        """
        charm_facade = client.CharmsFacade.from_connection(self.connection())
        res = await charm_facade.CharmInfo(entity_url)

        resources = []
        for resource in res.meta.resources.values():
            resources.append({
                'description': resource.description,
                'name': resource.name,
                'path': resource.path,
                'type_': resource.type_,
                'origin': 'store',
                'revision': -1,
            })

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

        resources_facade = client.ResourcesFacade.from_connection(
            self.connection())
        response = await resources_facade.AddPendingResources(
            application_tag=tag.application(application),
            charm_url=entity_url,
            charm_origin=origin,
            resources=[client.CharmResource(**resource) for resource in resources],
        )

        # response.pending_ids always exists but it can itself be None
        # see juju/client/_definitions.py for AddPendingResourcesResult
        resource_map = {resource['name']: pid
                        for resource, pid
                        in zip(resources, response.pending_ids or {})}

        return resource_map

    async def add_local_resources(self, application, entity_url, metadata, resources):
        """_add_local_resources is called by the deploy to add pending local  resources requested by
        the charm being deployed. It calls the ResourcesFacade.AddPendingResources. After getting
        the pending IDs from the controller it sends an HTTP PUT request to actually upload local
        resources.

        :param str application: the name of the application
        :param client.CharmURL entity_url: url for the charm that we add resources for
        :param [string]string metadata: metadata for the charm that we add resources for
        :param [string] resources: the paths for the local files (or oci-images) to be added as
        local resources

        :returns [string]string resource_map that is a map of resources to their assigned
        pendingIDs.
        """
        if not resources:
            return None

        resource_map = dict()

        for name, path in resources.items():
            resource_type = metadata["resources"][name]["type"]
            if resource_type not in {"oci-image", "file"}:
                log.info("Resource {} of type {} is not supported".format(name, resource_type))
                continue

            charmresource = {
                'description': '',
                'fingerprint': '',
                'name': name,
                'path': Path(path).name,
                'revision': 0,
                'size': 0,
                'type_': resource_type,
                'origin': 'upload',
            }

            resources_facade = client.ResourcesFacade.from_connection(
                self.connection())
            response = await resources_facade.AddPendingResources(
                application_tag=tag.application(application),
                charm_url=entity_url,
                resources=[client.CharmResource(**charmresource)])
            pending_id = response.pending_ids[0]
            resource_map[name] = pending_id

            if resource_type == "oci-image":
                # TODO Docker Image validation and support for local images.
                docker_image_details = {
                    'registrypath': path,
                    'username': '',
                    'password': '',
                }
                data = yaml.dump(docker_image_details)
            else:
                p = Path(path)
                data = p.read_text() if p.exists() else ''

            self._upload(data, path, application, name, resource_type, pending_id)

        return resource_map

    def _upload(self, data, path, app_name, res_name, res_type, pending_id):
        conn, headers, path_prefix = self.connection().https_connection()

        query = "?pendingid={}".format(pending_id)
        url = "{}/applications/{}/resources/{}{}".format(path_prefix, app_name, res_name, query)
        if res_type == "oci-image":
            disp = "multipart/form-data; filename=\"{}\"".format(path)
        else:
            disp = "form-data; filename=\"{}\"".format(path)

        headers['Content-Type'] = 'application/octet-stream'
        headers['Content-Length'] = len(data)
        headers['Content-Sha384'] = hashlib.sha384(bytes(data, 'utf-8')).hexdigest()
        headers['Content-Disposition'] = disp

        conn.request('PUT', url, data, headers)

        response = conn.getresponse()
        result = response.read().decode()
        if not response.status == 200:
            raise JujuError(result)

    async def _deploy(self, charm_url, application, series, config,
                      constraints, endpoint_bindings, resources, storage,
                      channel=None, num_units=None, placement=None,
                      devices=None, charm_origin=None, attach_storage=[],
                      force=False, server_side_deploy=False):
        """Logic shared between `Model.deploy` and `BundleHandler.deploy`.
        """
        log.info('Deploying %s', charm_url)

        trust = config.get('trust', False)
        # stringify all config values for API, and convert to YAML
        config = {k: str(v) for k, v in config.items()}
        config = yaml.dump({application: config},
                           default_flow_style=False)

        app_facade = client.ApplicationFacade.from_connection(self.connection())

        if server_side_deploy:
            # Call DeployFromRepository
            app = client.DeployFromRepositoryArg(
                applicationname=application,
                attachstorage=attach_storage,
                charmname=charm_url,
                configyaml=config,
                cons=parse_constraints(constraints),
                devices=devices,
                dryrun=False,
                placement=placement,
                storage=storage,
                trust=trust,
                base=charm_origin.base,
                channel=channel,
                endpoint_bindings=endpoint_bindings,
                force=force,
                num_units=num_units,
                resources=resources,
                revision=charm_origin.revision,
            )
            result = await app_facade.DeployFromRepository([app])
            # Collect the errors
            errors = []
            for r in result.results:
                if r.errors:
                    errors.extend([e.message for e in r.errors])
            # Upload pending local resources if any
            for _result in result.results:
                for pending_upload_resource in getattr(_result, 'pendingresourceuploads', []):
                    _path = pending_upload_resource.filename
                    p = Path(_path)
                    data = p.read_text() if p.exists() else ''
                    self._upload(data, _path, application, pending_upload_resource.name, 'file', '')
        else:
            app = client.ApplicationDeploy(
                charm_url=charm_url,
                application=application,
                series=series,
                channel=channel,
                charm_origin=charm_origin,
                config_yaml=config,
                constraints=parse_constraints(constraints),
                endpoint_bindings=endpoint_bindings,
                num_units=num_units,
                resources=resources,
                storage=storage,
                placement=placement,
                devices=devices,
                attach_storage=attach_storage,
                force=force,
            )
            result = await app_facade.Deploy(applications=[app])
            errors = [r.error.message for r in result.results if r.error]
        if errors:
            raise JujuError('\n'.join(errors))

        return await self._wait_for_new('application', application)

    async def destroy_unit(self, unit_id, destroy_storage=False, dry_run=False, force=False, max_wait=None):
        """Destroy units by name.

        """
        return await self.destroy_units(unit_id,
                                        destroy_storage=destroy_storage,
                                        dry_run=dry_run,
                                        force=force,
                                        max_wait=max_wait
                                        )

    async def destroy_units(self, *unit_names, destroy_storage=False, dry_run=False, force=False, max_wait=None):
        """Destroy several units at once.

        """
        connection = self.connection()
        app_facade = client.ApplicationFacade.from_connection(connection)

        units_to_destroy = []
        for unit_id in unit_names:
            unit_tag = tag.unit(unit_id)
            if unit_tag is None:
                log.error("Error converting %s to a valid unit tag", unit_id)
                raise JujuUnitError("Error converting %s to a valid unit tag", unit_id)
            units_to_destroy.append({
                'unit-tag': unit_tag,
                'destroy-storage': destroy_storage,
                'force': force,
                'max-wait': max_wait,
                'dry-run': dry_run,
            })
        log.debug('Destroying units %s', unit_names)
        return await app_facade.DestroyUnit(units=units_to_destroy)

    def download_backup(self, archive_id, target_filename=None):
        """Download a backup archive file.

        :param str archive_id: The id of the archive to download
        :param str (optional) target_filename: A custom name for the target file
        :return str: Path to the archive file

        """

        conn, headers, path_prefix = self.connection().https_connection()
        path = "%s/backups" % path_prefix
        headers['Content-Type'] = 'application/json'
        args = {'id': archive_id}
        conn.request("GET", path, json.dumps(args, indent=2), headers=headers)
        response = conn.getresponse()
        result = response.read()
        if not response.status == 200:
            raise JujuBackupError("unable to download the backup ID : %s -- got : %s from the JujuAPI with a HTTP response code : %s" % (archive_id, result, response.status))

        if target_filename:
            file_name = target_filename
        else:
            # check if archive_id is a filename
            if re.match(r'.*\.tar\.gz', archive_id):
                # if so, use the same ID generated & sent by the Juju API
                archive_id = re.compile('[0-9]+').findall(archive_id)[0]

            file_name = "juju-backup-%s.tar.gz" % archive_id

        with open(str(file_name), 'wb') as f:
            try:
                f.write(result)
            except (OSError, IOError) as e:
                raise JujuBackupError("backup ID : %s was fetched, but : %s" % (archive_id, e))

        log.info("Backup archive downloaded in : %s" % file_name)
        return file_name

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
            config[key] = client.ConfigValue.from_json(value)
        return config

    async def get_constraints(self):
        """Return the machine constraints for this model.

        :returns: A ``dict`` of constraints.
        """
        constraints = {}
        facade_cls = client.ModelConfigFacade

        facade = facade_cls.from_connection(self.connection())
        result = await facade.GetModelConstraints()

        # GetModelConstraints returns GetConstraintsResults which has a
        # 'constraints' attribute. If no constraints have been set
        # GetConstraintsResults.constraints is None. Otherwise
        # GetConstraintsResults.constraints has an attribute for each possible
        # constraint, each of these in turn will be None if they have not been
        # set.
        if result.constraints:
            constraint_types = [a for a in dir(result.constraints)
                                if a in client.Value._toSchema.keys()]
            for constraint in constraint_types:
                value = getattr(result.constraints, constraint)
                if value is not None:
                    constraints[constraint] = getattr(result.constraints,
                                                      constraint)
        return constraints

    async def get_machines(self):
        """Return list of machines in this model.

        """
        return list(self.state.machines.keys())

    async def get_spaces(self):
        """Return list of all known spaces, including associated subnets.

        Returns a List of :class:`~juju._definitions.Space` instances.
        """
        space_facade = client.SpacesFacade.from_connection(self.connection())
        response = await space_facade.ListSpaces()
        return response.results

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

    async def remove_backup(self, backup_id):
        """Delete a backup.

        :param str backup_id: The id of the backup to remove

        """
        backups_facade = client.BackupsFacade.from_connection(self.connection())
        return await backups_facade.Remove([backup_id])

    async def remove_backups(self, backup_ids):
        """Delete the given backups.

        :param [str] backup_ids: The list of ids of the backups to remove

        """
        backups_facade = client.BackupsFacade.from_connection(self.connection())
        return await backups_facade.Remove(backup_ids)

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
            self, backup_id, bootstrap=False,
            constraints=None, archive=None, upload_tools=False):
        """Restore a backup archive to a new controller.

        :param str backup_id: Id of backup to restore
        :param bool bootstrap: Bootstrap a new state machine
        :param constraints: Model constraints
        :type constraints: :class:`juju.Constraints`
        :param str archive: Path to backup archive to restore
        :param bool upload_tools: Upload tools if bootstrapping a new machine

        """
        raise DeprecationWarning("juju restore-backup is deprecated in favor of the stand-alone 'juju-restore' tool: https://github.com/juju/juju-restore")

    async def set_config(self, config):
        """Set configuration keys on this model.

        :param dict config: Mapping of config keys to either string values or
            `ConfigValue` instances, as returned by `get_config`.
        """
        config_facade = client.ModelConfigFacade.from_connection(
            self.connection()
        )

        new_conf = {}
        for key, value in config.items():
            if isinstance(value, client.ConfigValue):
                new_conf[key] = value.value
            elif isinstance(value, str):
                new_conf[key] = value
            else:
                raise JujuModelConfigError("Expected either a string or a ConfigValue as a config value, found : %s of type %s" % (value, type(value)))
        await config_facade.ModelSet(config=new_conf)

    async def set_constraints(self, constraints):
        """Set machine constraints on this model.

        :param dict config: Mapping of model constraints
        """

        facade_cls = client.ModelConfigFacade

        facade = facade_cls.from_connection(self.connection())

        await facade.SetModelConstraints(
            application='',
            constraints=constraints)

    async def get_action_output(self, action_uuid, wait=None):
        """ Get the results of an action by ID.

        :param str action_uuid: Id of the action
        :param int wait: Time in seconds to wait for action to complete.
        :return dict: Output from action
        :raises: :class:`JujuError` if invalid action_uuid
        """
        action = await self._get_completed_action(action_uuid, wait=wait)
        # ActionResult.output is None if the action produced no output
        return {} if action.output is None else action.output

    async def _get_completed_action(self, action_uuid, wait=None):
        """Get the completed internal _definitions.Action object.

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
                    await jasyncio.sleep(1)
        await jasyncio.wait_for(
            _wait_for_action_status(),
            timeout=wait)
        action_results = await action_facade.Actions(entities=entity)
        return action_results.results[0]

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

    async def get_status(self, filters=None, utc=False):
        """Return the status of the model.

        :param str filters: Optional list of applications, units, or machines
            to include, which can use wildcards ('*').
        :param bool utc: Display time as UTC in RFC3339 format

        """
        client_facade = client.ClientFacade.from_connection(self.connection())
        return await client_facade.FullStatus(patterns=filters)

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
        async with ConnectedController(self.connection()) as controller:
            return await controller.create_offer(self.info.uuid, endpoint,
                                                 offer_name=offer_name,
                                                 application_name=application_name)

    async def list_offers(self):
        """
        Offers list information about applications' endpoints that have been
        shared and who is connected.
        """
        async with ConnectedController(self.connection()) as controller:
            return await controller.list_offers(self.name)

    async def remove_offer(self, endpoint, force=False):
        """
        Remove offer for an application.

        Offers will also remove relations to those offers, use force to do
        so, without an error.
        """
        async with ConnectedController(self.connection()) as controller:
            return await controller.remove_offer(self.info.uuid, endpoint, force)

    async def consume(self, endpoint, application_alias="", controller_name=None, controller=None):
        """
        Adds a remote offer to the model. Relations can be created later using
        "juju relate".
        """
        if controller and controller_name:
            raise JujuError("cannot set both controller_name and controller")
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

        source = None
        if controller_name:
            source = await self._get_source_api(offer, controller_name=controller_name)
        else:
            if controller:
                source = controller
            else:
                source = Controller()
                kwargs = self.connection().connect_params()
                kwargs["uuid"] = None
                await source._connect_direct(**kwargs)

        consume_details = await source.get_consume_details(offer.as_local().string())

        # Only disconnect when the controller object has been created within
        # with function We don't want to disconnect the object passed by the
        # user in the controller argument
        if not controller:
            await source.disconnect()
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
            with open(str(filename), "w") as file:
                file.write(result.result)
        except IOError:
            raise

    async def add_secret(self, name, data_args, file="", info=""):
        """Adds a secret with a list of key values

        Equivalent to the cli command:
        juju add-secret [options] <name> [key[#base64|#file]=value...]

        :param name str: The name of the secret to be added.
        :param data_args []str: The key value pairs to be added into the secret.
        :param file str: A path to a yaml file containing secret key values.
        :param info str: The secret description.
        """
        data = create_secret_data(data_args)

        if file:
            data_from_file = read_secret_data(file)
            for k, v in data_from_file.items():
                # Caution: key/value pairs in files overwrite the ones in the args.
                data[k] = v

        if client.SecretsFacade.best_facade_version(self.connection()) < 2:
            raise JujuNotSupportedError("user secrets")

        secretsFacade = client.SecretsFacade.from_connection(self.connection())
        results = await secretsFacade.CreateSecrets([{
            'content': {'data': data},
            'description': info,
            'label': name,
        }])
        if len(results.results) != 1:
            raise JujuAPIError(f"expected 1 result, got {len(results.results)}")
        result = results.results[0]
        if result.error is not None:
            raise JujuAPIError(result.error.message)
        return result.result

    async def update_secret(self, name, data_args=[], new_name="", file="", info=""):
        """Update a secret with a list of key values, or info.

        Equivalent to the cli command:
        juju add-secret [options] <name> [key[#base64|#file]=value...]

        :param name str: The name of the secret to be added.
        :param data_args []str: The key value pairs to be added into the secret.
        :param file str: A path to a yaml file containing secret key values.
        :param info str: The secret description.
        """
        data = create_secret_data(data_args)
        if file:
            data_from_file = read_secret_data(file)
            for k, v in data_from_file.items():
                # Caution: key/value pairs in files overwrite the ones in the args.
                data[k] = v

        if client.SecretsFacade.best_facade_version(self.connection()) < 2:
            raise JujuNotSupportedError("user secrets")
        secretsFacade = client.SecretsFacade.from_connection(self.connection())
        results = await secretsFacade.UpdateSecrets([{
            'content': {'data': data},
            'description': info,
            'existing-label': name,
            'label': new_name,
        }])
        if len(results.results) != 1:
            raise JujuAPIError(f"expected 1 result, got {len(results.results)}")
        result_error = results.results[0]
        if result_error.error is not None:
            raise JujuAPIError(result_error.error)

    async def list_secrets(self, filter="", show_secrets=False):
        """
        Returns the list of available secrets.
        """
        facade = client.SecretsFacade.from_connection(self.connection())
        results = await facade.ListSecrets({
            'filter': filter,
            'show-secrets': show_secrets,
        })
        return results.results

    async def remove_secret(self, secret_name, revision=-1):
        """Remove an existing secret.

        :param secret_name str: ID|name of the secret to remove.
        :param revision int: remove the specified revision.
        """
        if client.SecretsFacade.best_facade_version(self.connection()) < 2:
            raise JujuNotSupportedError("user secrets")
        remove_secret_arg = {
            'label': secret_name,
        }
        if revision >= 0:
            remove_secret_arg['revisions'] = [revision]

        secretsFacade = client.SecretsFacade.from_connection(self.connection())
        results = await secretsFacade.RemoveSecrets([remove_secret_arg])
        if len(results.results) != 1:
            raise JujuAPIError(f"expected 1 result, got {len(results.results)}")
        result_error = results.results[0]
        if result_error.error is not None:
            raise JujuAPIError(result_error.error)

    async def grant_secret(self, secret_name, application, *applications):
        """Grants access to a secret to the specified applications.

        :param secret_name str: ID|name of the secret.
        :param application str: name of an application for which the access is granted
        :param applications []str: names of more applications to associate the secret with
        """
        if client.SecretsFacade.best_facade_version(self.connection()) < 2:
            raise JujuNotSupportedError("user secrets")
        secretsFacade = client.SecretsFacade.from_connection(self.connection())
        results = await secretsFacade.GrantSecret(
            applications=[application] + list(applications),
            label=secret_name)
        if len(results.results) != 1:
            raise JujuAPIError(f"expected 1 result, got {len(results.results)}")
        result_error = results.results[0]
        if result_error.error is not None:
            raise JujuAPIError(result_error.error)

    async def revoke_secret(self, secret_name, application, *applications):
        """Revoke access to a secret.

        Revoke applications' access to view the value of a specified secret.

        :param secret_name str: ID|name of the secret.
        :param application str: name of an application for which the access to the secret is revoked
        :param applications []str: names of more applications to disassociate the secret with
        """
        if client.SecretsFacade.best_facade_version(self.connection()) < 2:
            raise JujuNotSupportedError("user secrets")
        secretsFacade = client.SecretsFacade.from_connection(self.connection())
        results = await secretsFacade.RevokeSecret(
            applications=[application] + list(applications),
            label=secret_name)
        if len(results.results) != 1:
            raise JujuAPIError(f"expected 1 result, got {len(results.results)}")
        result_error = results.results[0]
        if result_error.error is not None:
            raise JujuAPIError(result_error.error)

    async def _get_source_api(self, url, controller_name=None):
        controller = Controller()
        if url.has_empty_source():
            async with ConnectedController(self.connection()) as current:
                if current.controller_name is not None:
                    controller_name = current.controller_name
        await controller.connect(controller_name=controller_name)
        return controller

    async def wait_for_idle(self, apps=None, raise_on_error=True, raise_on_blocked=False,
                            wait_for_active=False, timeout=10 * 60, idle_period=15, check_freq=0.5,
                            status=None, wait_for_at_least_units=None, wait_for_exact_units=None):
        """Wait for applications in the model to settle into an idle state.

        :param List[str] apps: Optional list of specific app names to wait on.
            If given, all apps must be present in the model and idle, while other
            apps in the model can still be busy. If not given, all apps currently
            in the model must be idle.

        :param bool raise_on_error: If True, then any unit or app going into
            "error" status immediately raises either a JujuAppError or a JujuUnitError.
            Note that machine or agent failures will always raise an exception (either
            JujuMachineError or JujuAgentError), regardless of this param. The default
            is True.

        :param bool raise_on_blocked: If True, then any unit or app going into
            "blocked" status immediately raises either a JujuAppError or a JujuUnitError.
            The default is False.

        :param bool wait_for_active: If True, then also wait for all unit workload
            statuses to be "active" as well. The default is False.

        :param float timeout: How long to wait, in seconds, for the bundle settles
            before raising an asyncio.TimeoutError. If None, will wait forever.
            The default is 10 minutes.

        :param float idle_period: How long, in seconds, the agent statuses of all
            units of all apps need to be `idle`. This delay is used to ensure that
            any pending hooks have a chance to start to avoid false positives.
            The default is 15 seconds.

        :param float check_freq: How frequently, in seconds, to check the model.
            The default is every half-second.

        :param str status: The status to wait for. If None, not waiting.
            The default is None (not waiting for any status).

        :param int wait_for_at_least_units: The least number of units to go into the idle
        state. wait_for_idle will return after that many units are available (across all the
        given applications).
            The default is 1 unit.

        :param int wait_for_exact_units: The exact number of units to be expected before
            going into the idle state. (e.g. useful for scaling down).
            When set, takes precedence over the `wait_for_units` parameter.
        """
        if wait_for_active:
            warnings.warn("wait_for_active is deprecated; use status", DeprecationWarning)
            status = "active"

        _wait_for_units = wait_for_at_least_units if wait_for_at_least_units is not None else 1

        timeout = timedelta(seconds=timeout) if timeout is not None else None
        idle_period = timedelta(seconds=idle_period)
        start_time = datetime.now()
        # Type check against the common error of passing a str for apps
        if apps is not None and (not isinstance(apps, list) or
                                 any(not isinstance(o, str)
                                     for o in apps)):
            raise JujuError(f'Expected a List[str] for apps, given {apps}')

        apps = apps or self.applications
        idle_times = {}
        units_ready = set()  # The units that are in the desired state
        last_log_time = None
        log_interval = timedelta(seconds=30)

        def _raise_for_status(entities, status):
            if not entities:
                return
            for entity_name, error_type in (("Machine", JujuMachineError),
                                            ("Agent", JujuAgentError),
                                            ("Unit", JujuUnitError),
                                            ("App", JujuAppError)):
                errored = entities.get(entity_name, [])
                if not errored:
                    continue
                raise error_type("{}{} in {}: {}".format(
                    entity_name,
                    "s" if len(errored) > 1 else "",
                    status,
                    ", ".join(errored),
                ))

        if wait_for_exact_units is not None:
            assert isinstance(wait_for_exact_units, int) and wait_for_exact_units >= 0, \
                'Invalid value for wait_for_exact_units : %s' % wait_for_exact_units

        while True:
            # The list 'busy' is what keeps this loop going,
            # i.e. it'll stop when busy is empty after all the
            # units are scanned
            busy = []
            errors = {}
            blocks = {}
            for app_name in apps:
                if app_name not in self.applications:
                    busy.append(app_name + " (missing)")
                    continue
                app = self.applications[app_name]
                app_status = await app.get_status()
                if raise_on_error and app_status == "error":
                    errors.setdefault("App", []).append(app.name)
                if raise_on_blocked and app_status == "blocked":
                    blocks.setdefault("App", []).append(app.name)

                # Check if wait_for_exact_units flag is used
                if wait_for_exact_units is not None:
                    if len(app.units) != wait_for_exact_units:
                        busy.append(app.name + " (waiting for exactly %s units, current : %s)" %
                                    (wait_for_exact_units, len(app.units)))
                        continue
                # If we have less # of units then required, then wait a bit more
                elif len(app.units) < _wait_for_units:
                    busy.append(app.name + " (not enough units yet - %s/%s)" %
                                (len(app.units), _wait_for_units))
                    continue
                # User is waiting for at least a certain # of units, and we have enough
                elif wait_for_at_least_units and len(units_ready) >= _wait_for_units:
                    # So no need to keep looking, we have the desired number of units ready to go,
                    # exit the loop. Don't just return here, though, we might still have some
                    # errors to raise at the end
                    break
                for unit in app.units:
                    if raise_on_error and unit.machine is not None and unit.machine.status == "error":
                        errors.setdefault("Machine", []).append(unit.machine.id)
                        continue
                    if raise_on_error and unit.agent_status == "error":
                        errors.setdefault("Agent", []).append(unit.name)
                        continue
                    if raise_on_error and unit.workload_status == "error":
                        errors.setdefault("Unit", []).append(unit.name)
                        continue
                    if raise_on_blocked and unit.workload_status == "blocked":
                        blocks.setdefault("Unit", []).append(unit.name)
                        continue
                    # TODO (cderici): we need two versions of wait_for_idle, one for waiting on
                    #  individual units, another one for waiting for an application.
                    #  The convoluted logic below is the result of trying to do both at the same
                    #  time
                    need_to_wait_more_for_a_particular_status = status and (unit.workload_status != status)
                    app_is_in_desired_status = (not status) or (app_status == status)
                    if not need_to_wait_more_for_a_particular_status and \
                            unit.agent_status == "idle" and \
                            (wait_for_at_least_units or app_is_in_desired_status):
                        # A unit is ready if either:
                        # 1) Don't need to wait more for a particular status and the agent is "idle"
                        # 2) We're looking for a particular status and the unit's workload,
                        # as well as the application, is in that status. If the user wants to
                        # see only a particular number of units in that state -- i.e. a subset of
                        # the units is needed, then we don't care about the application status
                        # (because e.g. app can be in 'waiting' while unit.0 is 'active' and unit.1
                        # is 'waiting')

                        # Either way, the unit is ready, start measuring the time period that
                        # it needs to stay in that state (i.e. idle_period)
                        units_ready.add(unit.name)
                        now = datetime.now()
                        idle_start = idle_times.setdefault(unit.name, now)

                        if now - idle_start < idle_period:
                            busy.append("{} [{}] {}: {}".format(unit.name,
                                                                unit.agent_status,
                                                                unit.workload_status,
                                                                unit.workload_status_message))
                    else:
                        idle_times.pop(unit.name, None)
                        busy.append("{} [{}] {}: {}".format(unit.name,
                                                            unit.agent_status,
                                                            unit.workload_status,
                                                            unit.workload_status_message))
            _raise_for_status(errors, "error")
            _raise_for_status(blocks, "blocked")
            if not busy:
                break
            busy = "\n  ".join(busy)
            if timeout is not None and datetime.now() - start_time > timeout:
                raise jasyncio.TimeoutError("Timed out waiting for model:\n" + busy)
            if last_log_time is None or datetime.now() - last_log_time > log_interval:
                log.info("Waiting for model:\n  " + busy)
                last_log_time = datetime.now()
            await jasyncio.sleep(check_freq)


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
        zf = zipfile.ZipFile(str(path), 'w', zipfile.ZIP_DEFLATED)
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
        s = os.stat(str(path))
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

    @staticmethod
    def type_name_override():
        return "model"
