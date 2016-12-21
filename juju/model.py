import asyncio
import collections
import logging
import os
import re
import weakref
from concurrent.futures import CancelledError
from functools import partial
from pathlib import Path

import yaml
from theblues import charmstore

from .client import client
from .client import watcher
from .client import connection
from .constraints import parse as parse_constraints, normalize_key
from .delta import get_entity_delta
from .delta import get_entity_class
from .exceptions import DeadEntityException
from .errors import JujuAPIError

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
    async def __call__(self, delta, old, new, model):
        handler_name = 'on_{}_{}'.format(delta.entity, delta.type)
        method = getattr(self, handler_name, self.on_change)
        await method(delta, old, new, model)

    async def on_change(self, delta, old, new, model):
        """Generic model-change handler.

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
        return self.safe_data[name]

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
    def __init__(self, loop=None):
        """Instantiate a new connected Model.

        :param loop: an asyncio event loop

        """
        self.loop = loop or asyncio.get_event_loop()
        self.connection = None
        self.observers = weakref.WeakValueDictionary()
        self.state = ModelState(self)
        self.info = None
        self._watcher_task = None
        self._watch_shutdown = asyncio.Event(loop=loop)
        self._watch_received = asyncio.Event(loop=loop)
        self._charmstore = CharmStore(self.loop)

    async def connect(self, *args, **kw):
        """Connect to an arbitrary Juju model.

        args and kw are passed through to Connection.connect()

        """
        self.connection = await connection.Connection.connect(*args, **kw)
        await self._after_connect()

    async def connect_current(self):
        """Connect to the current Juju model.

        """
        self.connection = await connection.Connection.connect_current()
        await self._after_connect()

    async def connect_model(self, model_name):
        """Connect to a specific Juju model by name.

        :param model_name:  Format [controller:][user/]model

        """
        self.connection = await connection.Connection.connect_model(model_name)
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
        self._stop_watching()
        if self.connection and self.connection.is_open:
            await self._watch_shutdown.wait()
            log.debug('Closing model connection')
            await self.connection.close()
            self.connection = None

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
                await asyncio.sleep(wait_period)
        await asyncio.wait_for(_block(), timeout)

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
        facade = client.ClientFacade()
        facade.connect(self.connection)

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
            self._watch_shutdown.clear()
            try:
                allwatcher = watcher.AllWatcher()
                self._watch_conn = await self.connection.clone()
                allwatcher.connect(self._watch_conn)
                while True:
                    results = await allwatcher.Next()
                    for delta in results.deltas:
                        delta = get_entity_delta(delta)
                        old_obj, new_obj = self.state.apply_delta(delta)
                        # XXX: Might not want to shield at this level
                        # We are shielding because when the watcher is
                        # canceled (on disconnect()), we don't want all of
                        # its children (every observer callback) to be
                        # canceled with it. So we shield them. But this means
                        # they can *never* be canceled.
                        await asyncio.shield(
                            self._notify_observers(delta, old_obj, new_obj))
                    self._watch_received.set()
            except CancelledError:
                log.debug('Closing watcher connection')
                await self._watch_conn.close()
                self._watch_shutdown.set()
                self._watch_conn = None

        log.debug('Starting watcher task')
        self._watcher_task = self.loop.create_task(_start_watch())

    def _stop_watching(self):
        """Stop the asynchronous watch against this model.

        """
        log.debug('Stopping watcher task')
        if self._watcher_task:
            self._watcher_task.cancel()

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
                asyncio.ensure_future(o(delta, old_obj, new_obj, self))

    async def _wait(self, entity_type, entity_id, action, predicate=None):
        """
        Block the calling routine until a given action has happened to the
        given entity

        :param entity_type: The entity's type.
        :param entity_id: The entity's id.
        :param action: the type of action (e.g., 'add' or 'change')
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
        return self.state._live_entity_map(entity_type)[entity_id]

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

    def add_machine(
            self, spec=None, constraints=None, disks=None, series=None,
            count=1):
        """Start a new, empty machine and optionally a container, or add a
        container to a machine.

        :param str spec: Machine specification
            Examples::

                (None) - starts a new machine
                'lxc' - starts a new machine with on lxc container
                'lxc:4' - starts a new lxc container on machine 4
                'ssh:user@10.10.0.3' - manually provisions a machine with ssh
                'zone=us-east-1a' - starts a machine in zone us-east-1s on AWS
                'maas2.name' - acquire machine maas2.name on MAAS
        :param constraints: Machine constraints
        :type constraints: :class:`juju.Constraints`
        :param list disks: List of disk :class:`constraints <juju.Constraints>`
        :param str series: Series
        :param int count: Number of machines to deploy

        Supported container types are: lxc, lxd, kvm

        When deploying a container to an existing machine, constraints cannot
        be used.

        """
        pass
    add_machines = add_machine

    async def add_relation(self, relation1, relation2):
        """Add a relation between two applications.

        :param str relation1: '<application>[:<relation_name>]'
        :param str relation2: '<application>[:<relation_name>]'

        """
        app_facade = client.ApplicationFacade()
        app_facade.connect(self.connection)

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
        pass

    def add_ssh_key(self, key):
        """Add a public SSH key to this model.

        :param str key: The public ssh key

        """
        pass
    add_ssh_keys = add_ssh_key

    def add_subnet(self, cidr_or_id, space, *zones):
        """Add an existing subnet to this model.

        :param str cidr_or_id: CIDR or provider ID of the existing subnet
        :param str space: Network space with which to associate
        :param str \*zones: Zone(s) in which the subnet resides

        """
        pass

    def get_backups(self):
        """Retrieve metadata for backups in this model.

        """
        pass

    def block(self, *commands):
        """Add a new block to this model.

        :param str \*commands: The commands to block. Valid values are
            'all-changes', 'destroy-model', 'remove-object'

        """
        pass

    def get_blocks(self):
        """List blocks for this model.

        """
        pass

    def get_cached_images(self, arch=None, kind=None, series=None):
        """Return a list of cached OS images.

        :param str arch: Filter by image architecture
        :param str kind: Filter by image kind, e.g. 'lxd'
        :param str series: Filter by image series, e.g. 'xenial'

        """
        pass

    def create_backup(self, note=None, no_download=False):
        """Create a backup of this model.

        :param str note: A note to store with the backup
        :param bool no_download: Do not download the backup archive
        :return str: Path to downloaded archive

        """
        pass

    def create_storage_pool(self, name, provider_type, **pool_config):
        """Create or define a storage pool.

        :param str name: Name to give the storage pool
        :param str provider_type: Pool provider type
        :param \*\*pool_config: key/value pool configuration pairs

        """
        pass

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
        pass

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
            the charm or bundle, e.g. 'development'
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
        :param str to: Placement directive, e.g.::

            '23' - machine 23
            'lxc:7' - new lxc container on machine 7
            '24/lxc/3' - lxc container 3 or machine 24

            If None, a new machine is provisioned.


        TODO::

            - application_name is required; fill this in automatically if not
              provided by caller
            - series is required; how do we pick a default?

        """
        if to:
            placement = [
                client.Placement(**p) for p in to
            ]
        else:
            placement = []

        if storage:
            storage = {
                k: client.Constraints(**v)
                for k, v in storage.items()
            }

        is_local = not entity_url.startswith('cs:') and \
            os.path.isdir(entity_url)
        entity_id = await self.charmstore.entityId(entity_url) \
            if not is_local else entity_url

        app_facade = client.ApplicationFacade()
        client_facade = client.ClientFacade()
        app_facade.connect(self.connection)
        client_facade.connect(self.connection)

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
                        self._wait_for_new('application', app_name))
                    for app_name in pending_apps
                ])
            return [app for name, app in self.applications.items()
                    if name in handler.applications]
        else:
            log.debug(
                'Deploying %s', entity_id)

            await client_facade.AddCharm(channel, entity_id)
            app = client.ApplicationDeploy(
                application=application_name,
                channel=channel,
                charm_url=entity_id,
                config=config,
                constraints=parse_constraints(constraints),
                endpoint_bindings=bind,
                num_units=num_units,
                placement=placement,
                resources=resources,
                series=series,
                storage=storage,
            )

            await app_facade.Deploy([app])
            return await self._wait_for_new('application', application_name)

    def destroy(self):
        """Terminate all machines and resources for this model.

        """
        pass

    async def destroy_unit(self, *unit_names):
        """Destroy units by name.

        """
        app_facade = client.ApplicationFacade()
        app_facade.connect(self.connection)

        log.debug(
            'Destroying unit%s %s',
            's' if len(unit_names) == 1 else '',
            ' '.join(unit_names))

        return await app_facade.Destroy(self.name)
    destroy_units = destroy_unit

    def get_backup(self, archive_id):
        """Download a backup archive file.

        :param str archive_id: The id of the archive to download
        :return str: Path to the archive file

        """
        pass

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
        pass

    def get_config(self):
        """Return the configuration settings for this model.

        """
        pass

    def get_constraints(self):
        """Return the machine constraints for this model.

        """
        pass

    def grant(self, username, acl='read'):
        """Grant a user access to this model.

        :param str username: Username
        :param str acl: Access control ('read' or 'write')

        """
        pass

    def import_ssh_key(self, identity):
        """Add a public SSH key from a trusted indentity source to this model.

        :param str identity: User identity in the form <lp|gh>:<username>

        """
        pass
    import_ssh_keys = import_ssh_key

    def get_machines(self, machine, utc=False):
        """Return list of machines in this model.

        :param str machine: Machine id, e.g. '0'
        :param bool utc: Display time as UTC in RFC3339 format

        """
        pass

    def get_shares(self):
        """Return list of all users with access to this model.

        """
        pass

    def get_spaces(self):
        """Return list of all known spaces, including associated subnets.

        """
        pass

    def get_ssh_key(self):
        """Return known SSH keys for this model.

        """
        pass
    get_ssh_keys = get_ssh_key

    def get_storage(self, filesystem=False, volume=False):
        """Return details of storage instances.

        :param bool filesystem: Include filesystem storage
        :param bool volume: Include volume storage

        """
        pass

    def get_storage_pools(self, names=None, providers=None):
        """Return list of storage pools.

        :param list names: Only include pools with these names
        :param list providers: Only include pools for these providers

        """
        pass

    def get_subnets(self, space=None, zone=None):
        """Return list of known subnets.

        :param str space: Only include subnets in this space
        :param str zone: Only include subnets in this zone

        """
        pass

    def remove_blocks(self):
        """Remove all blocks from this model.

        """
        pass

    def remove_backup(self, backup_id):
        """Delete a backup.

        :param str backup_id: The id of the backup to remove

        """
        pass

    def remove_cached_images(self, arch=None, kind=None, series=None):
        """Remove cached OS images.

        :param str arch: Architecture of the images to remove
        :param str kind: Image kind to remove, e.g. 'lxd'
        :param str series: Image series to remove, e.g. 'xenial'

        """
        pass

    def remove_machine(self, *machine_ids):
        """Remove a machine from this model.

        :param str \*machine_ids: Ids of the machines to remove

        """
        pass
    remove_machines = remove_machine

    def remove_ssh_key(self, *keys):
        """Remove a public SSH key(s) from this model.

        :param str \*keys: Keys to remove

        """
        pass
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
        pass

    def retry_provisioning(self):
        """Retry provisioning for failed machines.

        """
        pass

    def revoke(self, username, acl='read'):
        """Revoke a user's access to this model.

        :param str username: Username to revoke
        :param str acl: Access control ('read' or 'write')

        """
        pass

    def run(self, command, timeout=None):
        """Run command on all machines in this model.

        :param str command: The command to run
        :param int timeout: Time to wait before command is considered failed

        """
        pass

    def set_config(self, **config):
        """Set configuration keys on this model.

        :param \*\*config: Config key/values

        """
        pass

    def set_constraints(self, constraints):
        """Set machine constraints on this model.

        :param :class:`juju.Constraints` constraints: Machine constraints

        """
        pass

    def get_action_output(self, action_uuid, wait=-1):
        """Get the results of an action by ID.

        :param str action_uuid: Id of the action
        :param int wait: Time in seconds to wait for action to complete

        """
        pass

    def get_action_status(self, uuid_or_prefix=None, name=None):
        """Get the status of all actions, filtered by ID, ID prefix, or action name.

        :param str uuid_or_prefix: Filter by action uuid or prefix
        :param str name: Filter by action name

        """
        pass

    def get_budget(self, budget_name):
        """Get budget usage info.

        :param str budget_name: Name of budget

        """
        pass

    def get_status(self, filter_=None, utc=False):
        """Return the status of the model.

        :param str filter_: Service or unit name or wildcard ('*')
        :param bool utc: Display time as UTC in RFC3339 format

        """
        pass
    status = get_status

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
        pass

    def unblock(self, *commands):
        """Unblock an operation that would alter this model.

        :param str \*commands: The commands to unblock. Valid values are
            'all-changes', 'destroy-model', 'remove-object'

        """
        pass

    def unset_config(self, *keys):
        """Unset configuration on this model.

        :param str \*keys: The keys to unset

        """
        pass

    def upgrade_gui(self):
        """Upgrade the Juju GUI for this model.

        """
        pass

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
        pass

    def upload_backup(self, archive_path):
        """Store a backup archive remotely in Juju.

        :param str archive_path: Path to local archive

        """
        pass

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

        metrics_facade = client.MetricsDebugFacade()
        metrics_facade.connect(self.connection)

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
        self.client_facade = client.ClientFacade()
        self.client_facade.connect(model.connection)
        self.app_facade = client.ApplicationFacade()
        self.app_facade.connect(model.connection)
        self.ann_facade = client.AnnotationsFacade()
        self.ann_facade.connect(model.connection)

    async def fetch_plan(self, entity_id):
        is_local = not entity_id.startswith('cs:') and os.path.isdir(entity_id)
        if is_local:
            bundle_yaml = (Path(entity_id) / "bundle.yaml").read_text()
        else:
            bundle_yaml = await self.charmstore.files(entity_id,
                                                      filename='bundle.yaml',
                                                      read_file=True)
        self.bundle = yaml.safe_load(bundle_yaml)
        self.plan = await self.client_facade.GetBundleChanges(bundle_yaml)

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
            raise ValueError("Error adding machine: %s", error.message)
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
        # stringify all config values for API
        options = {k: str(v) for k, v in options.items()}
        # build param object
        app = client.ApplicationDeploy(
            charm_url=charm,
            series=series,
            application=application,
            config=options,
            constraints=parse_constraints(constraints),
            storage=storage,
            endpoint_bindings=endpoint_bindings,
            resources=resources,
        )
        # do the do
        log.info('Deploying %s', charm)
        await self.app_facade.Deploy([app])
        # ensure the app is in the model for future operations
        await self.model._wait_for_new('application', application)
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
        self._cs = charmstore.CharmStore()

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
                return await self.loop.run_in_executor(None, method)
            setattr(self, name, coro)
            wrapper = coro
        return wrapper
