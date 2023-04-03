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
from .errors import JujuAPIError, JujuError, JujuModelConfigError, JujuBackupError
from .errors import JujuModelError, JujuAppError, JujuUnitError, JujuAgentError, JujuMachineError, PylibjujuError
from .names import is_valid_application
from .offerendpoints import ParseError as OfferParseError
from .offerendpoints import parse_local_endpoint, parse_offer_url
from .origin import Channel, Source
from .placement import parse as parse_placement
from .tag import application as application_tag
from .url import URL, Schema
from .version import DEFAULT_ARCHITECTURE

log = logging.getLogger(__name__)

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

    async def resolve(self, url, architecture, app_name=None, channel=None, series=None, entity_url=None):
        """resolve attempts to resolve a local charm or bundle using the url
        and architecture. If information is missing, it will attempt to backfill
        that information, before sending the result back.
        """

        entity_url = url.path()
        entity_path = Path(entity_url)
        bundle_path = entity_path / 'bundle.yaml'

        identifier = entity_url
        origin = client.CharmOrigin(source="local", architecture=architecture)
        if not (entity_path.is_dir() or entity_path.is_file()):
            raise JujuError('{} path not found'.format(entity_url))

        is_bundle = (
            (entity_path.suffix == ".yaml" and entity_path.exists()) or
            bundle_path.exists()
        )

        if app_name is None:
            app_name = url.name

            if not is_bundle:
                entity_url = url.path()
                entity_path = Path(entity_url)
                if entity_path.suffix == '.charm':
                    with zipfile.ZipFile(str(entity_path), 'r') as charm_file:
                        metadata = yaml.load(charm_file.read('metadata.yaml'), Loader=yaml.FullLoader)
                else:
                    metadata_path = entity_path / 'metadata.yaml'
                    metadata = yaml.load(metadata_path.read_text(), Loader=yaml.FullLoader)
                app_name = metadata['name']

        return DeployTypeResult(
            identifier=identifier,
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

    async def resolve(self, url, architecture, app_name=None, channel=None, series=None, entity_url=None):
        """resolve attempts to resolve charmhub charms or bundles. A request to
        the charmhub API is required to correctly determine the charm url and
        underlying origin.
        """

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
                                    )

        charm_url_str, origin, supported_series = await self.charm_resolver(url, origin)
        charm_url = URL.parse(charm_url_str)

        if app_name is None:
            app_name = url.name

        if series:
            if series in supported_series:
                origin.series = series
                charm_url.series = series
            else:
                raise JujuError("Series {} not supported for {}. Only {}".format(series, url, supported_series))

        return DeployTypeResult(
            identifier=str(charm_url),
            app_name=app_name,
            origin=origin,
            is_bundle=origin.type_ == "bundle",
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
        self._info = None
        self._mode = None

        self._charmhub = CharmHub(self)

        self.deploy_types = {
            "local": LocalDeployType(),
            "ch": CharmhubDeployType(self._resolve_charm),
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

    def connect(self, *args, **kwargs):
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
        model_name = model_uuid = None
        if 'endpoint' not in kwargs and len(args) < 2:
            # Then we're using the model_name to pick the model
            if args and 'model_name' in kwargs:
                raise TypeError('connect() got multiple values for model_name')
            elif args:
                model_name = args[0]
            else:
                model_name = kwargs.pop('model_name', None)
            _, model_uuid = self._connector.connect_model(model_name, **kwargs)
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
            self._connector.connect(**kwargs)

    def connect_to(self, connection):
        conn_params = connection.connect_params()
        self._connect_direct(**conn_params)

    def _connect_direct(self, **kwargs):
        if self.info:
            uuid = self.info.uuid
        elif 'uuid' in kwargs:
            uuid = kwargs['uuid']
        else:
            raise PylibjujuError("Unable to find uuid for the model")
        self.disconnect()
        self._connector.connect(**kwargs)

    def disconnect(self):
        """Shut down the watcher task and close websockets.

        """

        if self.is_connected():
            log.debug('Closing model connection')
            self._connector.disconnect()
            self._info = None

    def add_local_charm_dir(self, charm_dir, series):
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
            charm_url = self.add_local_charm(fh, series, os.stat(str(fn)).st_size)

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

    def reset(self, force=False):
        """Reset the model to a clean state.

        :param bool force: Force-terminate machines.

        This returns only after the model has reached a clean state. "Clean"
        means no applications or machines exist in the model.

        """
        # TODO: Replace block_until with context managers!!! 
        log.debug('Resetting model')
        for app in self.applications.values():
            app.destroy()
        # self.block_until(
        #    lambda: len(self.applications) == 0
        #)
        for machine in self.machines.values():
            machine.destroy(force=force)
        # self.block_until(
        #    lambda: len(self.machines) == 0
        #)

    def create_storage_pool(self, name, provider_type, attributes=""):
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
        return storage_facade.CreatePool(pools=[client.StoragePool(
            name=name,
            provider=provider_type,
            attrs=dict(_attrs)
        )])

    def remove_storage_pool(self, name):
        """Remove an existing storage pool.

        :param str name:
        :return:
        """
        storage_facade = client.StorageFacade.from_connection(self.connection())
        return storage_facade.RemovePool(pools=[client.StoragePoolDeleteArg(name)])

    def update_storage_pool(self, name, attributes=""):
        """ Update storage pool attributes.

        :param name:
        :param attributes: "key=value key=value ..."
        :return:
        """
        _attrs = dict([splt.split("=") for splt in attributes.split()])
        if len(_attrs) == 0:
            raise JujuError("Expected at least one attribute to update")

        storage_facade = client.StorageFacade.from_connection(self.connection())
        return storage_facade.UpdatePool(pools=[client.StoragePool(
            name=name,
            attrs=_attrs,
        )])

    def list_storage(self, filesystem=False, volume=False):
        """Lists storage details.

        :param bool filesystem: List filesystem storage
        :param bool volume: List volume storage
        :return:
        """
        storage_facade = client.StorageFacade.from_connection(self.connection())

        if filesystem and volume:
            raise JujuError("--filesystem and --volume can not be used together")
        if filesystem:
            _res = storage_facade.ListFilesystems(filters=[client.FilesystemFilter()])
        elif volume:
            _res = storage_facade.ListVolumes(filters=[client.VolumeFilter()])
        else:
            _res = storage_facade.ListStorageDetails(filters=[client.StorageFilter()])

        err = _res.results[0].error
        res = _res.results[0].result

        if err is not None:
            raise JujuError(err.message)

        return [details.serialize() for details in res]

    def show_storage_details(self, *storage_ids):
        """Shows storage instance information.

        :param []str storage_ids:
        :return:
        """
        if not storage_ids:
            raise JujuError("Expected at least one storage ID")

        storage_facade = client.StorageFacade.from_connection(self.connection())
        res = storage_facade.StorageDetails(entities=[client.Entity(tag.storage(s)) for s in storage_ids])
        return [s.result.serialize() for s in res.results]

    def list_storage_pools(self):
        """List storage pools.

        :return:
        """
        # TODO (cderici): Filter on pool type, name.
        storage_facade = client.StorageFacade.from_connection(self.connection())
        res = storage_facade.ListPools(filters=[client.StoragePoolFilter()])
        err = res.results[0].error
        if err:
            raise JujuError(err.message)
        return [p.serialize() for p in res.results[0].storage_pools]

    def remove_storage(self, *storage_ids, force=False, destroy_storage=False):
        """Removes storage from the model.

        :param bool force: Remove storage even if it is currently attached
        :param bool destroy_storage: Remove the storage and destroy it
        :param []str storage_ids:
        :return:
        """
        if not storage_ids:
            raise JujuError("Expected at least one storage ID")

        storage_facade = client.StorageFacade.from_connection(self.connection())
        ret = storage_facade.Remove(storage=[client.RemoveStorageInstance(
            destroy_storage=destroy_storage,
            force=force,
            tag=s,
        ) for s in storage_ids])
        if ret.results[0].error:
            raise JujuError(ret.results[0].error.message)

    def remove_application(self, app_name, block_until_done=False, force=False, destroy_storage=False, no_wait=False):
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
        self.applications[app_name].remove(destroy_storage=destroy_storage,
                                                 force=force,
                                                 no_wait=no_wait,
                                                 )
        # TODO: Replace with context manager
        if block_until_done:
            self.block_until(lambda: app_name not in self.applications)

    def block_until(self, *conditions, timeout=None, wait_period=0.5):
        """Return only after all conditions are true.

        Raises `websockets.ConnectionClosed` if disconnected.
        """
        log.warning("the block_until function has to be refactored!!!!!")
        pass

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

    def add_machine(
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
        results = client_facade.AddMachines(params=[params])
        error = results.machines[0].error
        if error:
            raise ValueError("Error adding machine: %s" % error.message)
        machine_id = results.machines[0].machine

        if spec:
            if spec.startswith("ssh:"):
                # Need to run this after AddMachines has been called,
                # as we need the machine_id
                sshProvisioner.install_agent(
                    self.connection(),
                    params.nonce,
                    machine_id,
                )

        log.debug('Added new machine %s', machine_id)
        return self._wait_for_new('machine', machine_id)

    def add_relation(self, relation1, relation2):
        """
        .. deprecated:: 2.9.9
           Use ``relate()`` instead
        """
        return self.relate(relation1, relation2)

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
                with ConnectedController(self.connection()) as current:
                    remote_endpoint.source = current.controller_name
            # consume the remote endpoint
            self.consume(remote_endpoint.string(),
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
            result = app_facade.AddRelation(endpoints=endpoints, via_cidrs=None)
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

        self.block_until(lambda: _find_relation(*specs) is not None)
        return _find_relation(*specs)

    def relate(self, relation1, relation2):
        """The relate function is deprecated in favor of instead.
        The logic is the same.
        """
        log.warn("relate is deprecated and will be removed. Use integrate instead.")
        return self.integrate(relation1, relation2)

    def add_space(self, name, cidrs=None, public=True):
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
        return space_facade.CreateSpaces(spaces=spaces)

    def add_ssh_key(self, user, key):
        """Add a public SSH key to this model.

        :param str user: The username of the user
        :param str key: The public ssh key

        """
        key_facade = client.KeyManagerFacade.from_connection(self.connection())
        return key_facade.AddKeys(ssh_keys=[key], user=user)
    add_ssh_keys = add_ssh_key

    async def get_backups(self):
        """Retrieve metadata for backups in this model.

        :return [dict]: List of metadata for the stored backups
        """
        backups_facade = client.BackupsFacade.from_connection(self.connection())
        _backups_metadata = backups_facade.List()
        backups_metadata = _backups_metadata.serialize()
        if 'list' not in backups_metadata:
            raise JujuAPIError("Unexpected response metadata : %s" % backups_metadata)
        return backups_metadata['list']

    def create_backup(self, notes=None):
        """Create a backup of this model.

        :param str note: A note to store with the backup
        :param bool keep_copy: Keep a copy of the archive on the controller
        :param bool no_download: Do not download the backup archive
        :return str, dict: Filename for the downloaded archive file, Extra metadata for the created backup

        """
        backups_facade = client.BackupsFacade.from_connection(self.connection())
        results = backups_facade.Create(notes=notes)

        if results is None:
            raise JujuAPIError("unable to create a backup")

        backup_metadata = results.serialize()

        if 'error' in backup_metadata:
            raise JujuBackupError("unable to create a backup, got %s from Juju API" % backup_metadata)

        backup_id = backup_metadata['filename']

        file_name = self.download_backup(backup_id)

        return file_name, backup_metadata

    def debug_log(
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
            self.connect()

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
        self.connect(debug_log_conn=target, debug_log_params=params)

    def deploy(
            self, entity_url, application_name=None, bind=None,
            channel=None, config=None, constraints=None, force=False,
            num_units=1, overlays=[], base=None, resources=None, series=None,
            storage=None, to=None, devices=None, trust=False, attach_storage=[]):
        """Deploy a new service or bundle.

        :param str entity_url: Charm or bundle url
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
        :param dict storage: Storage constraints TODO how do these look?
        :param to: Placement directive as a string. For example:

            '23' - place on machine 23
            'lxd:7' - place in new lxd container on machine 7
            '24/lxd/3' - place in container 3 on machine 24

            If None, a new machine is provisioned.
        :param bool trust: Trust signifies that the charm should be deployed
            with access to trusted credentials. Hooks run by the charm can access
            cloud credentials and other trusted access credentials.

        :param str[] attach_storage: Existing storage to attach to the deployed unit
            (not available on k8s models)
        TODO::

            - support local file resources

        """
        if storage:
            storage = {
                k: client.Constraints(**v)
                for k, v in storage.items()
            }
        if trust and (self.info.agent_version < client.Number.from_json('2.4.0')):
            raise NotImplementedError("trusted is not supported on model version {}".format(self.info.agent_version))

        if not all([type(st) == str for st in attach_storage]):
            raise JujuError("Expected attach_storage to be a list of strings, given {}".format(attach_storage))

        # Ensure what we pass in, is a string.
        entity_url = str(entity_url)
        if is_local_charm(entity_url) and not entity_url.startswith("local:"):
            entity_url = "local:{}".format(entity_url)

        if client.CharmsFacade.best_facade_version(self.connection()) < 3:
            url = URL.parse(str(entity_url), default_store=Schema.CHARM_STORE)
        else:
            url = URL.parse(str(entity_url))

        architecture = self._resolve_architecture(url)

        if str(url.schema) not in self.deploy_types:
            raise JujuError("unknown deploy type {}, expected charmhub or local".format(url.schema))

        res = self.deploy_types[str(url.schema)].resolve(url, architecture, application_name, channel, series, entity_url)

        if res.identifier is None:
            raise JujuError('unknown charm or bundle {}'.format(entity_url))
        identifier = res.identifier

        charm_series = series
        charm_origin = res.origin
        if base:
            charm_origin.base = utils.parse_base_arg(base)

        if res.is_bundle:
            handler = BundleHandler(self, trusted=trust, forced=force)
            handler.fetch_plan(url, charm_origin, overlays=overlays)
            handler.execute_plan()
            extant_apps = {app for app in self.applications}
            pending_apps = handler.applications - extant_apps
            if pending_apps:
                # new apps will usually be in the model by now, but if some
                # haven't made it yet we'll need to wait on them to be added
                # TODO: refactor this to use context managers
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
                add_charm_res = self._add_charm(identifier, charm_origin)
                if isinstance(add_charm_res, dict):
                    # This is for backwards compatibility for older
                    # versions where AddCharm returns a dictionary
                    charm_origin = add_charm_res.get('charm_origin',
                                                     charm_origin)
                else:
                    charm_origin = add_charm_res.charm_origin
                if Schema.CHARM_HUB.matches(url.schema):
                    resources = self._add_charmhub_resources(res.app_name,
                                                                   identifier,
                                                                   add_charm_res.charm_origin)
                    is_sub = self.charmhub.is_subordinate(url.name)
                    if is_sub:
                        if num_units > 1:
                            raise JujuError("cannot use num_units with subordinate application")
                        num_units = 0

            else:
                # We have a local charm dir that needs to be uploaded
                charm_dir = os.path.abspath(os.path.expanduser(identifier))
                metadata = utils.get_local_charm_metadata(charm_dir)
                charm_series = charm_series or get_charm_series(metadata,
                                                                      self)
                if not base:
                    charm_origin.base = utils.get_local_charm_base(
                        charm_series, channel, metadata, charm_dir, client.Base)

                if not application_name:
                    application_name = metadata['name']
                if not application_name:
                    application_name = metadata['name']
                if base is None and charm_series is None:
                    raise JujuError(
                        "Either series or base is needed to deploy the "
                        "charm at {}. ".format(charm_dir))

                identifier = self.add_local_charm_dir(charm_dir,
                                                            charm_series)
                resources = self.add_local_resources(application_name,
                                                           identifier,
                                                           metadata,
                                                           resources=resources)

            if config is None:
                config = {}
            if trust:
                config["trust"] = "true"

            return self._deploy(
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
            )

    def _add_charm(self, charm_url, origin):
        # client facade is deprecated with in Juju, and smaller, more focused
        # facades have been created and we'll use that if it's available.
        charms_cls = client.CharmsFacade
        if charms_cls.best_facade_version(self.connection()) > 2:
            charms_facade = charms_cls.from_connection(self.connection())
            return charms_facade.AddCharm(charm_origin=origin, url=charm_url, force=False)

        client_facade = client.ClientFacade.from_connection(self.connection())
        return client_facade.AddCharm(channel=str(origin.risk), url=charm_url, force=False)

    def _resolve_charm(self, url, origin):
        """Calls Charms.ResolveCharms to resolve all the fields of the
        charm_origin and also the url and the supported_series

        :param str url: The url of the charm
        :param client.CharmOrigin origin: The manually constructed origin
        based on what we know about the charm and the deployment so far

        Returns the confirmed origin returned by the Juju API to be used in
        calls like ApplicationFacade.Deploy

        :returns str, client.CharmOrigin, [str]
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
                          'base': origin.base}

        resp = charms_facade.ResolveCharms(resolve=[{
            'reference': str(url),
            'charm-origin': resolve_origin
        }])
        if len(resp.results) != 1:
            raise JujuError("expected one result, received {}".format(resp.results))

        result = resp.results[0]
        if result.error:
            raise JujuError(result.error.message)

        return (result.url, result.charm_origin, result.supported_series)

    def _resolve_architecture(self, url):
        if url.architecture:
            return url.architecture

        constraints = self.get_constraints()
        if 'arch' in constraints:
            return constraints['arch']

        return DEFAULT_ARCHITECTURE

    def _add_charmhub_resources(self, application,
                                      entity_url,
                                      origin,
                                      overrides=None):
        charm_facade = client.CharmsFacade.from_connection(self.connection())
        res = charm_facade.CharmInfo(entity_url)

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
        response = resources_facade.AddPendingResources(
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

    def add_local_resources(self, application, entity_url, metadata, resources):
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
            response = resources_facade.AddPendingResources(
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

                hash_alg = hashlib.sha3_384

                charmresource['fingerprint'] = hash_alg(bytes(data, 'utf-8')).digest()

                conn, headers, path_prefix = self.connection().https_connection()

                query = "?pendingid={}".format(pending_id)
                url = "{}/applications/{}/resources/{}{}".format(
                    path_prefix, application, name, query)
                if resource_type == "oci-image":
                    disp = "multipart/form-data; filename=\"{}\"".format(path)
                else:
                    disp = "form-data; filename=\"{}\"".format(path)

                headers['Content-Type'] = 'application/octet-stream'
                headers['Content-Length'] = len(data)
                headers['Content-Sha384'] = charmresource['fingerprint'].hex()
                headers['Content-Disposition'] = disp

                conn.request('PUT', url, data, headers)

                response = conn.getresponse()
                result = response.read().decode()
                if not response.status == 200:
                    raise JujuError(result)

        return resource_map

    def _deploy(self, charm_url, application, series, config,
                      constraints, endpoint_bindings, resources, storage,
                      channel=None, num_units=None, placement=None,
                      devices=None, charm_origin=None, attach_storage=[]):
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
        )
        result = app_facade.Deploy(applications=[app])
        errors = [r.error.message for r in result.results if r.error]
        if errors:
            raise JujuError('\n'.join(errors))
        return self._wait_for_new('application', application)

    def destroy_unit(self, unit_id, destroy_storage=False, dry_run=False, force=False, max_wait=None):
        """Destroy units by name.

        """
        connection = self.connection()
        app_facade = client.ApplicationFacade.from_connection(connection)

        # Get the corresponding unit tag
        unit_tag = tag.unit(unit_id)
        if unit_tag is None:
            log.error("Error converting %s to a valid unit tag", unit_id)
            return JujuUnitError("Error converting %s to a valid unit tag", unit_id)

        log.debug(
            'Destroying unit %s', unit_id)

        return app_facade.DestroyUnit(units=[{
            'unit-tag': unit_tag,
            'destroy-storage': destroy_storage,
            'force': force,
            'max-wait': max_wait,
            'dry-run': dry_run,
        }])

    def destroy_units(self, *unit_names, destroy_storage=False, dry_run=False, force=False, max_wait=None):
        """Destroy several units at once.

        """
        for u in unit_names:
            self.destroy_unit(u, destroy_storage, dry_run, force, max_wait)

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

    def get_config(self):
        """Return the configuration settings for this model.

        :returns: A ``dict`` mapping keys to `ConfigValue` instances,
            which have `source` and `value` attributes.
        """
        config_facade = client.ModelConfigFacade.from_connection(
            self.connection()
        )
        result = config_facade.ModelGet()
        config = result.config
        for key, value in config.items():
            config[key] = client.ConfigValue.from_json(value)
        return config

    def get_constraints(self):
        """Return the machine constraints for this model.

        :returns: A ``dict`` of constraints.
        """
        constraints = {}
        facade_cls = client.ModelConfigFacade

        facade = facade_cls.from_connection(self.connection())
        result = facade.GetModelConstraints()

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
        response = space_facade.ListSpaces()
        return response.results

    async def get_ssh_key(self, raw_ssh=False):
        """Return known SSH keys for this model.
        :param bool raw_ssh: if True, returns the raw ssh key,
            else it's fingerprint

        """
        key_facade = client.KeyManagerFacade.from_connection(self.connection())
        entity = {'tag': tag.model(self.info.uuid)}
        entities = client.Entities([entity])
        return key_facade.ListKeys(entities=entities, mode=raw_ssh)
    get_ssh_keys = get_ssh_key

    async def remove_backup(self, backup_id):
        """Delete a backup.

        :param str backup_id: The id of the backup to remove

        """
        backups_facade = client.BackupsFacade.from_connection(self.connection())
        return backups_facade.Remove([backup_id])

    async def remove_backups(self, backup_ids):
        """Delete the given backups.

        :param [str] backup_ids: The list of ids of the backups to remove

        """
        backups_facade = client.BackupsFacade.from_connection(self.connection())
        return backups_facade.Remove(backup_ids)

    def remove_ssh_key(self, user, key):
        """Remove a public SSH key(s) from this model.

        :param str key: Full ssh key
        :param str user: Juju user to which the key is registered

        """
        key_facade = client.KeyManagerFacade.from_connection(self.connection())
        key = base64.b64decode(bytes(key.strip().split()[1].encode('ascii')))
        key = hashlib.md5(key).hexdigest()
        key = ':'.join(a + b for a, b in zip(key[::2], key[1::2]))
        key_facade.DeleteKeys(ssh_keys=[key], user=user)
    remove_ssh_keys = remove_ssh_key

    def set_config(self, config):
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
        config_facade.ModelSet(config=new_conf)

    def set_constraints(self, constraints):
        """Set machine constraints on this model.

        :param dict config: Mapping of model constraints
        """

        facade_cls = client.ModelConfigFacade

        facade = facade_cls.from_connection(self.connection())

        facade.SetModelConstraints(
            application='',
            constraints=constraints)

    def get_action_output(self, action_uuid, wait=None):
        """ Get the results of an action by ID.

        :param str action_uuid: Id of the action
        :param int wait: Time in seconds to wait for action to complete.
        :return dict: Output from action
        :raises: :class:`JujuError` if invalid action_uuid
        """
        action = self._get_completed_action(action_uuid, wait=wait)
        # ActionResult.output is None if the action produced no output
        return {} if action.output is None else action.output

    def _get_completed_action(self, action_uuid, wait=None):
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

        def _wait_for_action_status():
            while True:
                action_output = action_facade.Actions(entities=entity)
                if action_output.results[0].status in ('completed', 'failed'):
                    return
                else:
                    time.sleep(1)
        # TODO: replace with context manager
        jasyncio.wait_for(
            _wait_for_action_status(),
            timeout=wait)
        action_results = action_facade.Actions(entities=entity)
        return action_results.results[0]

    def get_action_status(self, uuid_or_prefix=None, name=None):
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
            name_results = action_facade.FindActionsByNames(names=[name])
            action_results.extend(name_results.actions[0].actions)
        if uuid_or_prefix:
            # Collect list of actions matching uuid or prefix
            matching_actions = action_facade.FindActionTagsByPrefix(
                prefixes=[uuid_or_prefix])
            entities = []
            for actions in matching_actions.matches.values():
                entities = [{'tag': a.tag} for a in actions]
            # Get action results matching action tags
            uuid_results = action_facade.Actions(entities=entities)
            action_results.extend(uuid_results.results)
        for a in action_results:
            results[tag.untag('action-', a.action.tag)] = a.status
        return results

    def get_status(self, filters=None, utc=False):
        """Return the status of the model.

        :param str filters: Optional list of applications, units, or machines
            to include, which can use wildcards ('*').
        :param bool utc: Display time as UTC in RFC3339 format

        """
        client_facade = client.ClientFacade.from_connection(self.connection())
        return client_facade.FullStatus(patterns=filters)

    def get_metrics(self, *tags):
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
        metrics_result = metrics_facade.GetMetrics(entities=entities)

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

    def create_offer(self, endpoint, offer_name=None, application_name=None):
        """
        Offer a deployed application using a series of endpoints for use by
        consumers.

        @param endpoint: holds the application and endpoint you want to offer
        @param offer_name: over ride the offer name to help the consumer
        """
        with ConnectedController(self.connection()) as controller:
            return controller.create_offer(self.info.uuid, endpoint,
                                                 offer_name=offer_name,
                                                 application_name=application_name)

    def list_offers(self):
        """
        Offers list information about applications' endpoints that have been
        shared and who is connected.
        """
        with ConnectedController(self.connection()) as controller:
            return controller.list_offers(self.name)

    def remove_offer(self, endpoint, force=False):
        """
        Remove offer for an application.

        Offers will also remove relations to those offers, use force to do
        so, without an error.
        """
        with ConnectedController(self.connection()) as controller:
            return controller.remove_offer(self.info.uuid, endpoint, force)

    def consume(self, endpoint, application_alias="", controller_name=None, controller=None):
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
            source = self._get_source_api(offer, controller_name=controller_name)
        else:
            if controller:
                source = controller
            else:
                source = Controller()
                kwargs = self.connection().connect_params()
                kwargs["uuid"] = None
                source._connect_direct(**kwargs)

        consume_details = source.get_consume_details(offer.as_local().string())

        # Only disconnect when the controller object has been created within
        # with function We don't want to disconnect the object passed by the
        # user in the controller argument
        if not controller:
            source.disconnect()
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
        results = facade.Consume(args=[arg])
        if len(results.results) != 1:
            raise JujuAPIError("expected 1 result, recieved {}".format(len(results.results)))
        if results.results[0].error is not None:
            raise JujuAPIError(results.results[0].error)
        local_name = offer_url.application
        if application_alias != "":
            local_name = application_alias
        return local_name

    def remove_saas(self, name):
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
        return facade.DestroyConsumedApplications(applications=[arg])

    def export_bundle(self, filename=None):
        """
        Exports the current model configuration as a reusable bundle.
        """
        facade = client.BundleFacade.from_connection(self.connection())
        result = facade.ExportBundle()
        if result.error is not None:
            raise JujuAPIError(result.error)

        if filename is None:
            return result.result

        try:
            with open(str(filename), "w") as file:
                file.write(result.result)
        except IOError:
            raise

    def list_secrets(self, filter="", show_secrets=False):
        """
        Returns the list of available secrets.
        """
        facade = client.SecretsFacade.from_connection(self.connection())
        return facade.ListSecrets({
            'filter': filter,
            'show-secrets': show_secrets,
        })

    def _get_source_api(self, url, controller_name=None):
        controller = Controller()
        if url.has_empty_source():
            with ConnectedController(self.connection()) as current:
                if current.controller_name is not None:
                    controller_name = current.controller_name
        controller.connect(controller_name=controller_name)
        return controller

    async def wait_for_idle(self, apps=None, raise_on_error=True, raise_on_blocked=False,
                            wait_for_active=False, timeout=10 * 60, idle_period=15, check_freq=0.5,
                            status=None, wait_for_units=1, wait_for_exact_units=None):
        """Wait for applications in the model to settle into an idle state.

        :param apps (list[str]): Optional list of specific app names to wait on.
            If given, all apps must be present in the model and idle, while other
            apps in the model can still be busy. If not given, all apps currently
            in the model must be idle.

        :param raise_on_error (bool): If True, then any unit or app going into
            "error" status immediately raises either a JujuAppError or a JujuUnitError.
            Note that machine or agent failures will always raise an exception (either
            JujuMachineError or JujuAgentError), regardless of this param. The default
            is True.

        :param raise_on_blocked (bool): If True, then any unit or app going into
            "blocked" status immediately raises either a JujuAppError or a JujuUnitError.
            The defaul tis False.

        :param wait_for_active (bool): If True, then also wait for all unit workload
            statuses to be "active" as well. The default is False.

        :param timeout (float): How long to wait, in seconds, for the bundle settles
            before raising an asyncio.TimeoutError. If None, will wait forever.
            The default is 10 minutes.

        :param idle_period (float): How long, in seconds, the agent statuses of all
            units of all apps need to be `idle`. This delay is used to ensure that
            any pending hooks have a chance to start to avoid false positives.
            The default is 15 seconds.

        :param check_freq (float): How frequently, in seconds, to check the model.
            The default is every half-second.

        :param status (str): The status to wait for. If None, not waiting.
            The default is None (not waiting for any status).

        :param wait_for_units (int): The least number of units to be expected before
            going into the idle state.
            The default is 1 unit.

        :param wait_for_exact_units (int): The exact number of units to be expected before
            going into the idle state. (e.g. useful for scaling down).
            When set, takes precedence over the `wait_for_units` parameter.
        """
        if wait_for_active:
            warnings.warn("wait_for_active is deprecated; use status", DeprecationWarning)
            status = "active"

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
            assert type(wait_for_exact_units) == int and wait_for_exact_units >= 0, \
                'Invalid value for wait_for_exact_units : %s' % wait_for_exact_units

        while True:
            busy = []
            errors = {}
            blocks = {}
            for app_name in apps:
                if app_name not in self.applications:
                    busy.append(app_name + " (missing)")
                    continue
                app = self.applications[app_name]
                if raise_on_error and app.status == "error":
                    errors.setdefault("App", []).append(app.name)
                if raise_on_blocked and app.status == "blocked":
                    blocks.setdefault("App", []).append(app.name)
                if wait_for_exact_units is not None:
                    if len(app.units) != wait_for_exact_units:
                        busy.append(app.name + " (waiting for exactly %s units, current : %s)" %
                                    (wait_for_exact_units, len(app.units)))
                        continue
                elif len(app.units) < wait_for_units:
                    busy.append(app.name + " (not enough units yet - %s/%s)" %
                                (len(app.units), wait_for_units))
                    continue
                for unit in app.units:
                    if unit.machine is not None and unit.machine.status == "error":
                        errors.setdefault("Machine", []).append(unit.machine.id)
                        continue
                    if unit.agent_status == "error":
                        errors.setdefault("Agent", []).append(unit.name)
                        continue
                    if raise_on_error and unit.workload_status == "error":
                        errors.setdefault("Unit", []).append(unit.name)
                        continue
                    if raise_on_blocked and unit.workload_status == "blocked":
                        blocks.setdefault("Unit", []).append(unit.name)
                        continue
                    waiting_for_status = status and unit.workload_status != status
                    if not waiting_for_status and unit.agent_status == "idle":
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
