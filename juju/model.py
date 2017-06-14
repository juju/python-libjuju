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

from . import tag, utils
from .client import client
from .client import connection
from .constraints import parse as parse_constraints, normalize_key
from .delta import get_entity_delta
from .delta import get_entity_class
from .exceptions import DeadEntityException
from .errors import JujuError, JujuAPIError
from .placement import parse as parse_placement

log = logging.getLogger(__name__)


class _Observer(object):
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


class ModelObserver(object):
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


class ModelState(object):
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


class ModelEntity(object):
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
        self.connection = model.connection

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
        return self.__class__.__name__.lower()

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


class Model(object):
    """
    The main API for interacting with a Juju model.
    """
    def __init__(self, loop=None):
        """Instantiate a new connected Model.

        :param loop: an asyncio event loop

        """
        self.loop = loop or asyncio.get_event_loop()
        self.connection = None
        self.observers = weakref.WeakValueDictionary()
        self.state = ModelState(self)
        self.info = None
        self._watch_stopping = asyncio.Event(loop=self.loop)
        self._watch_stopped = asyncio.Event(loop=self.loop)
        self._watch_received = asyncio.Event(loop=self.loop)
        self._charmstore = CharmStore(self.loop)

    async def __aenter__(self):
        await self.connect_current()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

        if exc_type is not None:
            return False

    async def connect(self, *args, **kw):
        """Connect to an arbitrary Juju model.

        args and kw are passed through to Connection.connect()

        """
        if 'loop' not in kw:
            kw['loop'] = self.loop
        self.connection = await connection.Connection.connect(*args, **kw)
        await self._after_connect()

    async def connect_current(self):
        """Connect to the current Juju model.

        """
        self.connection = await connection.Connection.connect_current(
            self.loop)
        await self._after_connect()

    async def connect_model(self, model_name):
        """Connect to a specific Juju model by name.

        :param model_name:  Format [controller:][user/]model

        """
        self.connection = await connection.Connection.connect_model(model_name,
                                                                    self.loop)
        await self._after_connect()

    async def _after_connect(self):
        """Run initialization steps after connecting to websocket.

        """
        self._watch()
        await self._watch_received.wait()
        await self.get_info()

    async def disconnect(self):
        """Shut down the watcher task and close websockets.

        """
        if self.connection and self.connection.is_open:
            log.debug('Stopping watcher task')
            self._watch_stopping.set()
            await self._watch_stopped.wait()
            log.debug('Closing model connection')
            await self.connection.close()
            self.connection = None

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
            charm_url = await self.loop.run_in_executor(None, func)

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
        conn, headers, path_prefix = self.connection.https_connection()
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

        """
        async def _block():
            while not all(c() for c in conditions):
                await asyncio.sleep(wait_period, loop=self.loop)
        await asyncio.wait_for(_block(), timeout, loop=self.loop)

    @property
    def applications(self):
        """Return a map of application-name:Application for all applications
        currently in the model.

        """
        return self.state.applications

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
        facade = client.ClientFacade.from_connection(self.connection)

        self.info = await facade.ModelInfo()
        log.debug('Got ModelInfo: %s', vars(self.info))

        return self.info

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
        self.observers[observer] = callable_

    def _watch(self):
        """Start an asynchronous watch against this model.

        See :meth:`add_observer` to register an onchange callback.

        """
        async def _start_watch():
            try:
                allwatcher = client.AllWatcherFacade.from_connection(
                    self.connection)
                while not self._watch_stopping.is_set():
                    results = await utils.run_with_interrupt(
                        allwatcher.Next(),
                        self._watch_stopping,
                        self.loop)
                    if self._watch_stopping.is_set():
                        break
                    for delta in results.deltas:
                        delta = get_entity_delta(delta)
                        old_obj, new_obj = self.state.apply_delta(delta)
                        await self._notify_observers(delta, old_obj, new_obj)
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
        self.loop.create_task(_start_watch())

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

        for o in self.observers:
            if o.cares_about(delta):
                asyncio.ensure_future(o(delta, old_obj, new_obj, self),
                                      loop=self.loop)

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
        q = asyncio.Queue(loop=self.loop)

        async def callback(delta, old, new, model):
            await q.put(delta.get_id())

        self.add_observer(callback, entity_type, action, entity_id, predicate)
        entity_id = await q.get()
        # object might not be in the entity_map if we were waiting for a
        # 'remove' action
        return self.state._live_entity_map(entity_type).get(entity_id)

    async def _wait_for_new(self, entity_type, entity_id=None, predicate=None):
        """Wait for a new object to appear in the Model and return it.

        Waits for an object of type ``entity_type`` with id ``entity_id``.
        If ``entity_id`` is ``None``, it will wait for the first new entity
        of the correct type.

        This coroutine blocks until the new object appears in the model.

        """
        # if the entity is already in the model, just return it
        if entity_id in self.state._live_entity_map(entity_type):
            return self.state._live_entity_map(entity_type)[entity_id]
        # if we know the entity_id, we can trigger on any action that puts
        # the enitty into the model; otherwise, we have to watch for the
        # next "add" action on that entity_type
        action = 'add' if entity_id is None else None
        return await self._wait(entity_type, entity_id, action, predicate)

    async def wait_for_action(self, action_id):
        """Given an action, wait for it to complete."""

        if action_id.startswith("action-"):
            # if we've been passed action.tag, transform it into the
            # id that the api deltas will use.
            action_id = action_id[7:]

        def predicate(delta):
            return delta.data['status'] in ('completed', 'failed')

        return await self._wait('action', action_id, 'change', predicate)

    async def add_machine(
            self, spec=None, constraints=None, disks=None, series=None):
        """Start a new, empty machine and optionally a container, or add a
        container to a machine.

        :param str spec: Machine specification
            Examples::

                (None) - starts a new machine
                'lxd' - starts a new machine with one lxd container
                'lxd:4' - starts a new lxd container on machine 4
                'ssh:user@10.10.0.3' - manually provisions a machine with ssh
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
        params.jobs = ['JobHostUnits']

        if spec:
            placement = parse_placement(spec)
            if placement:
                params.placement = placement[0]

        if constraints:
            params.constraints = client.Value.from_json(constraints)

        if disks:
            params.disks = [
                client.Constraints.from_json(o) for o in disks]

        if series:
            params.series = series

        # Submit the request.
        client_facade = client.ClientFacade.from_connection(self.connection)
        results = await client_facade.AddMachines([params])
        error = results.machines[0].error
        if error:
            raise ValueError("Error adding machine: %s" % error.message)
        machine_id = results.machines[0].machine
        log.debug('Added new machine %s', machine_id)
        return await self._wait_for_new('machine', machine_id)

    async def add_relation(self, relation1, relation2):
        """Add a relation between two applications.

        :param str relation1: '<application>[:<relation_name>]'
        :param str relation2: '<application>[:<relation_name>]'

        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Adding relation %s <-> %s', relation1, relation2)

        try:
            result = await app_facade.AddRelation([relation1, relation2])
        except JujuAPIError as e:
            if 'relation already exists' not in e.message:
                raise
            log.debug(
                'Relation %s <-> %s already exists', relation1, relation2)
            # TODO: if relation already exists we should return the
            # Relation ModelEntity here
            return None

        def predicate(delta):
            endpoints = {}
            for endpoint in delta.data['endpoints']:
                endpoints[endpoint['application-name']] = endpoint['relation']
            return endpoints == result.endpoints

        return await self._wait_for_new('relation', None, predicate)

    def add_space(self, name, *cidrs):
        """Add a new network space.

        Adds a new space with the given name and associates the given
        (optional) list of existing subnet CIDRs with it.

        :param str name: Name of the space
        :param \*cidrs: Optional list of existing subnet CIDRs

        """
        raise NotImplementedError()

    async def add_ssh_key(self, user, key):
        """Add a public SSH key to this model.

        :param str user: The username of the user
        :param str key: The public ssh key

        """
        key_facade = client.KeyManagerFacade.from_connection(self.connection)
        return await key_facade.AddKeys([key], user)
    add_ssh_keys = add_ssh_key

    def add_subnet(self, cidr_or_id, space, *zones):
        """Add an existing subnet to this model.

        :param str cidr_or_id: CIDR or provider ID of the existing subnet
        :param str space: Network space with which to associate
        :param str \*zones: Zone(s) in which the subnet resides

        """
        raise NotImplementedError()

    def get_backups(self):
        """Retrieve metadata for backups in this model.

        """
        raise NotImplementedError()

    def block(self, *commands):
        """Add a new block to this model.

        :param str \*commands: The commands to block. Valid values are
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
        :param \*\*pool_config: key/value pool configuration pairs

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
            to=None):
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


        TODO::

            - support local resources

        """
        if storage:
            storage = {
                k: client.Constraints(**v)
                for k, v in storage.items()
            }

        is_local = (
            entity_url.startswith('local:') or
            os.path.isdir(entity_url)
        )
        if is_local:
            entity_id = entity_url.replace('local:', '')
        else:
            entity = await self.charmstore.entity(entity_url, channel=channel)
            entity_id = entity['Id']

        client_facade = client.ClientFacade.from_connection(self.connection)

        is_bundle = ((is_local and
                      (Path(entity_id) / 'bundle.yaml').exists()) or
                     (not is_local and 'bundle/' in entity_id))

        if is_bundle:
            handler = BundleHandler(self)
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
                        loop=self.loop)
                    for app_name in pending_apps
                ], loop=self.loop)
            return [app for name, app in self.applications.items()
                    if name in handler.applications]
        else:
            if not is_local:
                if not application_name:
                    application_name = entity['Meta']['charm-metadata']['Name']
                if not series:
                    series = self._get_series(entity_url, entity)
                await client_facade.AddCharm(channel, entity_id)
                # XXX: we're dropping local resources here, but we don't
                # actually support them yet anyway
                resources = await self._add_store_resources(application_name,
                                                            entity_id,
                                                            entity)
            else:
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
            return await self._deploy(
                charm_url=entity_id,
                application=application_name,
                series=series,
                config=config or {},
                constraints=constraints,
                endpoint_bindings=bind,
                resources=resources,
                storage=storage,
                channel=channel,
                num_units=num_units,
                placement=parse_placement(to)
            )

    async def _add_store_resources(self, application, entity_url, entity=None):
        if not entity:
            # avoid extra charm store call if one was already made
            entity = await self.charmstore.entity(entity_url)
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

        if not resources:
            return None

        resources_facade = client.ResourcesFacade.from_connection(
            self.connection)
        response = await resources_facade.AddPendingResources(
            tag.application(application),
            entity_url,
            [client.CharmResource(**resource) for resource in resources])
        resource_map = {resource['name']: pid
                        for resource, pid
                        in zip(resources, response.pending_ids)}
        return resource_map

    async def _deploy(self, charm_url, application, series, config,
                      constraints, endpoint_bindings, resources, storage,
                      channel=None, num_units=None, placement=None):
        """Logic shared between `Model.deploy` and `BundleHandler.deploy`.
        """
        log.info('Deploying %s', charm_url)

        # stringify all config values for API, and convert to YAML
        config = {k: str(v) for k, v in config.items()}
        config = yaml.dump({application: config},
                           default_flow_style=False)

        app_facade = client.ApplicationFacade.from_connection(
            self.connection)

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
            placement=placement
        )

        result = await app_facade.Deploy([app])
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
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Destroying unit%s %s',
            's' if len(unit_names) == 1 else '',
            ' '.join(unit_names))

        return await app_facade.DestroyUnits(list(unit_names))
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

    def get_config(self):
        """Return the configuration settings for this model.

        """
        raise NotImplementedError()

    def get_constraints(self):
        """Return the machine constraints for this model.

        """
        raise NotImplementedError()

    async def grant(self, username, acl='read'):
        """Grant a user access to this model.

        :param str username: Username
        :param str acl: Access control ('read' or 'write')

        """
        controller_conn = await self.connection.controller()
        model_facade = client.ModelManagerFacade.from_connection(
            controller_conn)
        user = tag.user(username)
        model = tag.model(self.info.uuid)
        changes = client.ModifyModelAccess(acl, 'grant', model, user)
        await self.revoke(username)
        return await model_facade.ModifyModelAccess([changes])

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
        key_facade = client.KeyManagerFacade.from_connection(self.connection)
        entity = {'tag': tag.model(self.info.uuid)}
        entities = client.Entities([entity])
        return await key_facade.ListKeys(entities, raw_ssh)
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

        :param str \*machine_ids: Ids of the machines to remove

        """
        raise NotImplementedError()
    remove_machines = remove_machine

    async def remove_ssh_key(self, user, key):
        """Remove a public SSH key(s) from this model.

        :param str key: Full ssh key
        :param str user: Juju user to which the key is registered

        """
        key_facade = client.KeyManagerFacade.from_connection(self.connection)
        key = base64.b64decode(bytes(key.strip().split()[1].encode('ascii')))
        key = hashlib.md5(key).hexdigest()
        key = ':'.join(a+b for a, b in zip(key[::2], key[1::2]))
        await key_facade.DeleteKeys([key], user)
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

    async def revoke(self, username):
        """Revoke a user's access to this model.

        :param str username: Username to revoke

        """
        controller_conn = await self.connection.controller()
        model_facade = client.ModelManagerFacade.from_connection(
            controller_conn)
        user = tag.user(username)
        model = tag.model(self.info.uuid)
        changes = client.ModifyModelAccess('read', 'revoke', model, user)
        return await model_facade.ModifyModelAccess([changes])

    def run(self, command, timeout=None):
        """Run command on all machines in this model.

        :param str command: The command to run
        :param int timeout: Time to wait before command is considered failed

        """
        raise NotImplementedError()

    def set_config(self, **config):
        """Set configuration keys on this model.

        :param \*\*config: Config key/values

        """
        raise NotImplementedError()

    def set_constraints(self, constraints):
        """Set machine constraints on this model.

        :param :class:`juju.Constraints` constraints: Machine constraints

        """
        raise NotImplementedError()

    def get_action_output(self, action_uuid, wait=-1):
        """Get the results of an action by ID.

        :param str action_uuid: Id of the action
        :param int wait: Time in seconds to wait for action to complete

        """
        raise NotImplementedError()

    def get_action_status(self, uuid_or_prefix=None, name=None):
        """Get the status of all actions, filtered by ID, ID prefix, or action name.

        :param str uuid_or_prefix: Filter by action uuid or prefix
        :param str name: Filter by action name

        """
        raise NotImplementedError()

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
        client_facade = client.ClientFacade.from_connection(self.connection)
        return await client_facade.FullStatus(filters)

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

        :param str \*commands: The commands to unblock. Valid values are
            'all-changes', 'destroy-model', 'remove-object'

        """
        raise NotImplementedError()

    def unset_config(self, *keys):
        """Unset configuration on this model.

        :param str \*keys: The keys to unset

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

        :param str \*tags: Tags of entities from which to retrieve metrics.
            No tags retrieves the metrics of all units in the model.
        :return: Dictionary of unit_name:metrics

        """
        log.debug("Retrieving metrics for %s",
                  ', '.join(tags) if tags else "all units")

        metrics_facade = client.MetricsDebugFacade.from_connection(
            self.connection)

        entities = [client.Entity(tag) for tag in tags]
        metrics_result = await metrics_facade.GetMetrics(entities)

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


def get_charm_series(path):
    """Inspects the charm directory at ``path`` and returns a default
    series from its metadata.yaml (the first item in the 'series' list).

    Returns None if no series can be determined.

    """
    md = Path(path) / "metadata.yaml"
    if not md.exists():
        return None
    data = yaml.load(md.open())
    series = data.get('series')
    return series[0] if series else None


class BundleHandler(object):
    """
    Handle bundles by using the API to translate bundle YAML into a plan of
    steps and then dispatching each of those using the API.
    """
    def __init__(self, model):
        self.model = model
        self.charmstore = model.charmstore
        self.plan = []
        self.references = {}
        self._units_by_app = {}
        for unit_name, unit in model.units.items():
            app_units = self._units_by_app.setdefault(unit.application, [])
            app_units.append(unit_name)
        self.client_facade = client.ClientFacade.from_connection(
            model.connection)
        self.app_facade = client.ApplicationFacade.from_connection(
            model.connection)
        self.ann_facade = client.AnnotationsFacade.from_connection(
            model.connection)

    async def _handle_local_charms(self, bundle):
        """Search for references to local charms (i.e. filesystem paths)
        in the bundle. Upload the local charms to the model, and replace
        the filesystem paths with appropriate 'local:' paths in the bundle.

        Return the modified bundle.

        :param dict bundle: Bundle dictionary
        :return: Modified bundle dictionary

        """
        apps, args = [], []

        default_series = bundle.get('series')
        for app_name in self.applications:
            app_dict = bundle['services'][app_name]
            charm_dir = os.path.abspath(os.path.expanduser(app_dict['charm']))
            if not os.path.isdir(charm_dir):
                continue
            series = (
                app_dict.get('series') or
                default_series or
                get_charm_series(charm_dir)
            )
            if not series:
                raise JujuError(
                    "Couldn't determine series for charm at {}. "
                    "Add a 'series' key to the bundle.".format(charm_dir))

            # Keep track of what we need to update. We keep a list of apps
            # that need to be updated, and a corresponding list of args
            # needed to update those apps.
            apps.append(app_name)
            args.append((charm_dir, series))

        if apps:
            # If we have apps to update, spawn all the coroutines concurrently
            # and wait for them to finish.
            charm_urls = await asyncio.gather(*[
                self.model.add_local_charm_dir(*params)
                for params in args
            ], loop=self.model.loop)
            # Update the 'charm:' entry for each app with the new 'local:' url.
            for app_name, charm_url in zip(apps, charm_urls):
                bundle['services'][app_name]['charm'] = charm_url

        return bundle

    async def fetch_plan(self, entity_id):
        is_local = not entity_id.startswith('cs:') and os.path.isdir(entity_id)
        if is_local:
            bundle_yaml = (Path(entity_id) / "bundle.yaml").read_text()
        else:
            bundle_yaml = await self.charmstore.files(entity_id,
                                                      filename='bundle.yaml',
                                                      read_file=True)
        self.bundle = yaml.safe_load(bundle_yaml)
        self.bundle = await self._handle_local_charms(self.bundle)

        self.plan = await self.client_facade.GetBundleChanges(
            yaml.dump(self.bundle))

    async def execute_plan(self):
        for step in self.plan.changes:
            method = getattr(self, step.method)
            result = await method(*step.args)
            self.references[step.id_] = result

    @property
    def applications(self):
        return list(self.bundle['services'].keys())

    def resolve(self, reference):
        if reference and reference.startswith('$'):
            reference = self.references[reference[1:]]
        return reference

    async def addCharm(self, charm, series):
        """
        :param charm string:
            Charm holds the URL of the charm to be added.

        :param series string:
            Series holds the series of the charm to be added
            if the charm default is not sufficient.
        """
        # We don't add local charms because they've already been added
        # by self._handle_local_charms
        if charm.startswith('local:'):
            return charm

        entity_id = await self.charmstore.entityId(charm)
        log.debug('Adding %s', entity_id)
        await self.client_facade.AddCharm(None, entity_id)
        return entity_id

    async def addMachines(self, params=None):
        """
        :param params dict:
            Dictionary specifying the machine to add. All keys are optional.
            Keys include:

            series: string specifying the machine OS series.

            constraints: string holding machine constraints, if any. We'll
                parse this into the json friendly dict that the juju api
                expects.

            container_type: string holding the type of the container (for
                instance ""lxd" or kvm"). It is not specified for top level
                machines.

            parent_id: string holding a placeholder pointing to another
                machine change or to a unit change. This value is only
                specified in the case this machine is a container, in
                which case also ContainerType is set.

        """
        params = params or {}

        # Normalize keys
        params = {normalize_key(k): params[k] for k in params.keys()}

        # Fix up values, as necessary.
        if 'parent_id' in params:
            params['parent_id'] = self.resolve(params['parent_id'])

        params['constraints'] = parse_constraints(
            params.get('constraints'))
        params['jobs'] = params.get('jobs', ['JobHostUnits'])

        if params.get('container_type') == 'lxc':
            log.warning('Juju 2.0 does not support lxc containers. '
                        'Converting containers to lxd.')
            params['container_type'] = 'lxd'

        # Submit the request.
        params = client.AddMachineParams(**params)
        results = await self.client_facade.AddMachines([params])
        error = results.machines[0].error
        if error:
            raise ValueError("Error adding machine: %s" % error.message)
        machine = results.machines[0].machine
        log.debug('Added new machine %s', machine)
        return machine

    async def addRelation(self, endpoint1, endpoint2):
        """
        :param endpoint1 string:
        :param endpoint2 string:
            Endpoint1 and Endpoint2 hold relation endpoints in the
            "application:interface" form, where the application is always a
            placeholder pointing to an application change, and the interface is
            optional. Examples are "$deploy-42:web" or just "$deploy-42".
        """
        endpoints = [endpoint1, endpoint2]
        # resolve indirect references
        for i in range(len(endpoints)):
            parts = endpoints[i].split(':')
            parts[0] = self.resolve(parts[0])
            endpoints[i] = ':'.join(parts)

        log.info('Relating %s <-> %s', *endpoints)
        return await self.model.add_relation(*endpoints)

    async def deploy(self, charm, series, application, options, constraints,
                     storage, endpoint_bindings, resources):
        """
        :param charm string:
            Charm holds the URL of the charm to be used to deploy this
            application.

        :param series string:
            Series holds the series of the application to be deployed
            if the charm default is not sufficient.

        :param application string:
            Application holds the application name.

        :param options map[string]interface{}:
            Options holds application options.

        :param constraints string:
            Constraints holds the optional application constraints.

        :param storage map[string]string:
            Storage holds the optional storage constraints.

        :param endpoint_bindings map[string]string:
            EndpointBindings holds the optional endpoint bindings

        :param resources map[string]int:
            Resources identifies the revision to use for each resource
            of the application's charm.
        """
        # resolve indirect references
        charm = self.resolve(charm)
        # the bundle plan doesn't actually do anything with resources, even
        # though it ostensibly gives us something (None) for that param
        if not charm.startswith('local:'):
            resources = await self.model._add_store_resources(application,
                                                              charm)
        await self.model._deploy(
            charm_url=charm,
            application=application,
            series=series,
            config=options,
            constraints=constraints,
            endpoint_bindings=endpoint_bindings,
            resources=resources,
            storage=storage,
        )
        return application

    async def addUnit(self, application, to):
        """
        :param application string:
            Application holds the application placeholder name for which a unit
            is added.

        :param to string:
            To holds the optional location where to add the unit, as a
            placeholder pointing to another unit change or to a machine change.
        """
        application = self.resolve(application)
        placement = self.resolve(to)
        if self._units_by_app.get(application):
            # enough units for this application already exist;
            # claim one, and carry on
            # NB: this should probably honor placement, but the juju client
            # doesn't, so we're not bothering, either
            unit_name = self._units_by_app[application].pop()
            log.debug('Reusing unit %s for %s', unit_name, application)
            return self.model.units[unit_name]

        log.debug('Adding new unit for %s%s', application,
                  ' to %s' % placement if placement else '')
        return await self.model.applications[application].add_unit(
            count=1,
            to=placement,
        )

    async def expose(self, application):
        """
        :param application string:
            Application holds the placeholder name of the application that must
            be exposed.
        """
        application = self.resolve(application)
        log.info('Exposing %s', application)
        return await self.model.applications[application].expose()

    async def setAnnotations(self, id_, entity_type, annotations):
        """
        :param id_ string:
            Id is the placeholder for the application or machine change
            corresponding to the entity to be annotated.

        :param entity_type EntityType:
            EntityType holds the type of the entity, "application" or
            "machine".

        :param annotations map[string]string:
            Annotations holds the annotations as key/value pairs.
        """
        entity_id = self.resolve(id_)
        try:
            entity = self.model.state.get_entity(entity_type, entity_id)
        except KeyError:
            entity = await self.model._wait_for_new(entity_type, entity_id)
        return await entity.set_annotations(annotations)


class CharmStore(object):
    """
    Async wrapper around theblues.charmstore.CharmStore
    """
    def __init__(self, loop):
        self.loop = loop
        self._cs = theblues.charmstore.CharmStore(timeout=5)

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


class CharmArchiveGenerator(object):
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

            * build/\* - This is used for packing the charm itself and any
                          similar tasks.
            * \*/.\*    - Hidden files are all ignored for now.  This will most
                          likely be changed into a specific ignore list
                          (.bzr, etc)

        """
        zf = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
        for dirpath, dirnames, filenames in os.walk(self.path):
            relative_path = dirpath[len(self.path) + 1:]
            if relative_path and not self._ignore(relative_path):
                zf.write(dirpath, relative_path)
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
        raise ValueError("Invalid Charm at % %s" % (
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
