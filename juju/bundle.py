import asyncio
import logging
import os
from pathlib import Path

import yaml

from toposort import toposort_flatten

from .client import client
from .constraints import parse as parse_constraints, parse_storage_constraint, parse_device_constraint
from .errors import JujuError

log = logging.getLogger(__name__)


class BundleHandler:
    """
    Handle bundles by using the API to translate bundle YAML into a plan of
    steps and then dispatching each of those using the API.
    """
    def __init__(self, model, trusted=False, forced=False):
        self.model = model
        self.trusted = trusted
        self.forced = forced

        self.charmstore = model.charmstore
        self.plan = []
        self.references = {}
        self._units_by_app = {}

        for unit_name, unit in model.units.items():
            app_units = self._units_by_app.setdefault(unit.application, [])
            app_units.append(unit_name)
        self.bundle_facade = client.BundleFacade.from_connection(
            model.connection())
        self.client_facade = client.ClientFacade.from_connection(
            model.connection())
        self.app_facade = client.ApplicationFacade.from_connection(
            model.connection())
        self.ann_facade = client.AnnotationsFacade.from_connection(
            model.connection())

        # This describes all the change types that the BundleHandler supports.
        change_type_cls = [AddApplicationChange,
                           AddCharmChange,
                           AddMachineChange,
                           AddRelationChange,
                           AddUnitChange,
                           CreateOfferChange,
                           ConsumeOfferChange,
                           ExposeChange,
                           ScaleChange,
                           SetAnnotationsChange]
        self.change_types = {}
        for change_cls in change_type_cls:
            self.change_types[change_cls.method()] = change_cls

    async def _validate_bundle(self, bundle):
        """Validate the bundle for known issues, raises an error if it
        encounters a known problem
        """
        apps_dict = bundle.get('applications', bundle.get('services', {}))
        for app_name in self.applications:
            app_dict = apps_dict[app_name]
            app_trusted = app_dict.get('trust')
            if (not self.trusted and not self.forced) and app_trusted:
                raise JujuError(
                    "Bundle cannot be deployed without trusting applications with your cloud credentials.\n"
                    "Please repeat the deploy command with the --trust argument if you consent to trust the following application\n"
                    " - {}\n".format(app_name)
                )
        return bundle

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
        apps_dict = bundle.get('applications', bundle.get('services', {}))
        for app_name in self.applications:
            app_dict = apps_dict[app_name]
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
                apps_dict[app_name]['charm'] = charm_url

        return bundle

    async def fetch_plan(self, entity_id):
        is_store_url = entity_id.startswith('cs:')

        if not is_store_url and os.path.isfile(entity_id):
            bundle_yaml = Path(entity_id).read_text()
        elif not is_store_url and os.path.isdir(entity_id):
            bundle_yaml = (Path(entity_id) / "bundle.yaml").read_text()
        else:
            bundle_yaml = await self.charmstore.files(entity_id,
                                                      filename='bundle.yaml',
                                                      read_file=True)
        self.bundle = yaml.safe_load(bundle_yaml)
        self.bundle = await self._validate_bundle(self.bundle)
        self.bundle = await self._handle_local_charms(self.bundle)

        self.plan = await self.bundle_facade.GetChanges(
            bundleurl=entity_id,
            yaml=yaml.dump(self.bundle))

        if self.plan.errors:
            raise JujuError(self.plan.errors)

    async def execute_plan(self):
        changes = ChangeSet(self.plan.changes)
        for step in changes.sorted():
            change_cls = self.change_types.get(step.method)
            if change_cls is None:
                raise NotImplementedError("unknown change type: {}".format(step.method))
            change = change_cls(step.id_, step.requires, step.args)
            log.info("Applying change: {}".format(change))
            self.references[step.id_] = await change.run(self)

    @property
    def applications(self):
        apps_dict = self.bundle.get('applications',
                                    self.bundle.get('services', {}))
        return list(apps_dict.keys())

    def resolveRelation(self, reference):
        parts = reference.split(":", maxsplit=1)
        application = self.resolve(parts[0])
        if len(parts) == 1:
            return application
        return "{}:{}".format(application, parts[1])

    def resolve(self, reference):
        if reference and reference.startswith('$'):
            ref = self.references[reference[1:]]
            if ref is not None:
                reference = ref
        return reference


def get_charm_series(path):
    """Inspects the charm directory at ``path`` and returns a default
    series from its metadata.yaml (the first item in the 'series' list).

    Returns None if no series can be determined.
    """
    md = Path(path) / "metadata.yaml"
    if not md.exists():
        return None
    try:
        data = yaml.safe_load(md.open())
    except yaml.YAMLError as exc:
        if hasattr(exc, "problem_mark"):
            mark = exc.problem_mark
            log.error("Error parsing YAML file {}, line {}, column: {}".format(md, mark.line, mark.column))
        raise
    series = data.get('series')
    return series[0] if series else None


class ChangeSet:

    def __init__(self, changes):
        self.changes = changes

    # sorted does a topological sort of the changes
    def sorted(self):
        if len(self.changes) == 0:
            return []

        changes = {}
        for change in self.changes:
            changes[change.id_] = set(change.requires)
        sorted_changes = toposort_flatten(changes)
        results = []
        for change_id in sorted_changes:
            for change in self.changes:
                if change_id == change.id_:
                    results.append(change)
                    break
        return results


class ChangeInfo:
    _toPy = {}

    def __init__(self, change_id, requires):
        self.change_id = change_id
        self.requires = requires

    @classmethod
    def from_dict(cls, self, data):
        """from_dict converts a data bag into fields on a class instance.
        If a value is missing from the data, then None is assigned to the field
        instance value.
        """
        d = (data or {})
        for k, v in cls._toPy.items():
            if k in d:
                setattr(self, v, d[k])
            else:
                setattr(self, v, None)


class AddApplicationChange(ChangeInfo):
    _toPy = {'charm': 'charm',
             'series': 'series',
             'application': 'application',
             'options': 'options',
             'constraints': 'constraints',
             'storage': 'storage',
             'devices': 'devices',
             'endpoint-bindings': 'endpoint_bindings',
             'resources': 'resources',
             'num-units': 'num_units'}

    """AddApplicationChange holds a change for deploying a Juju application.

    :charm: URL of the charm to be used to deploy this application.
    :series: series of the application to be deployed if the charm
        default is not sufficient.
    :application: application name.
    :num_units: number of units required. For IAAS models, this will
        be 0 and separate AddUnitChanges will be used. For Kubernetes models,
        this will be used to scale the application.
    :options: holds application options.
    :constraints: optional application constraints.
    :storage: optional storage constraints.
    :devices: optional devices constraints.
    :endpoint_bindings: optional endpoint bindings
    :resources: identifies the revision to use for each resource of the
        application's charm.
    :local_resources: identifies the path to the local resource of the
        application's charm.
    """
    def __init__(self, change_id, requires, params=None):
        super(AddApplicationChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.charm = params[0]
            self.series = params[1]
            self.application = params[2]
            self.options = params[3]
            self.constraints = params[4]
            self.storage = {k: parse_storage_constraint(v) for k, v in params[5].items()}
            if len(params) == 8:
                # Juju 2.4 and below only sends the endpoint bindings and resources
                self.endpoint_bindings = params[6]
                self.resources = params[7]
                self.devices = None
                self.num_units = None
            else:
                # Juju 2.5+ sends devices before endpoint bindings, as well as num_units
                # There might be placement but we need to ignore that.
                self.devices = {k: parse_device_constraint(v) for k, v in params[6].items()}
                self.endpoint_bindings = params[7]
                self.resources = params[8]
                self.num_units = params[9]

        elif isinstance(params, dict):
            AddApplicationChange.from_dict(self, params)
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        """method returns an associated ID for the Juju API call.
        """
        return "deploy"

    async def run(self, context):
        """Executes a AddApplicationChange using the returned parameters from
        the API server.

        :param context: is used for any methods or properties required to
            perform a change.
        """
        # resolve indirect references
        charm = context.resolve(self.charm)
        options = {}
        if self.options is not None:
            options = self.options
        if context.trusted:
            if context.model.info.agent_version < client.Number.from_json('2.4.0'):
                raise NotImplementedError("trusted is not supported on model version {}".format(context.model.info.agent_version))
            options["trust"] = "true"
        if not charm.startswith('local:'):
            resources = await context.model._add_store_resources(
                self.application, charm, overrides=self.resources)
        else:
            resources = {}
        await context.model._deploy(
            charm_url=charm,
            application=self.application,
            series=self.series,
            config=options,
            constraints=self.constraints,
            endpoint_bindings=self.endpoint_bindings,
            resources=resources,
            storage=self.storage,
            devices=self.devices,
            num_units=self.num_units,
        )
        return self.application

    def __str__(self):
        series = ""
        if self.series is not None and self.series != "":
            series = " on {}".format(self.series)
        units_info = ""
        if self.num_units is not None:
            plural = ""
            if self.num_units > 1:
                plural = "s"
            units_info = " with {num_units} unit{plural}".format(num_units=self.num_units,
                                                                 plural=plural)
        return "deploy application {application}{units_info}{series} using {charm}".format(application=self.application,
                                                                                           units_info=units_info,
                                                                                           series=series,
                                                                                           charm=self.charm)


class AddCharmChange(ChangeInfo):
    _toPy = {'charm': 'charm',
             'series': 'series',
             'channel': 'channel'}

    """AddCharmChange holds a change for adding a charm to the environment.

    :change_id: id of the change that will be used to identify the current
        change
    :requires: is a slice of dependencies that are required to happen.
    :params: holds the change parameters from the api response. Currently the
        params could either be a list or a dict. The later being the newer
        return results.

    Params holds the following values:
        :charm: URL of the charm to be added.
        :series: series of the charm to be added if the charm default is
           not sufficient.
        :channel: preferred channel for obtaining the charm.
    """
    def __init__(self, change_id, requires, params=None):
        super(AddCharmChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.charm = params[0]
            self.series = params[1]
            if len(params) > 2 and params[2] != "":
                self.channel = params[2]
            else:
                self.channel = None
        elif isinstance(params, dict):
            AddCharmChange.from_dict(self, params)
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        """method returns an associated ID for the Juju API call.
        """
        return "addCharm"

    async def run(self, context):
        """Executes a AddCharmChange using the returned parameters from
        the API server.

        :param context: is used for any methods or properties required to
            perform a change.
        """
        # We don't add local charms because they've already been added
        # by self._handle_local_charms
        if self.charm.startswith('local:'):
            return self.charm

        entity_id = await context.charmstore.entityId(self.charm)
        log.debug('Adding %s', entity_id)
        await context.client_facade.AddCharm(channel=None, url=entity_id, force=False)
        return entity_id

    def __str__(self):
        series = ""
        channel = ""
        if self.series is not None and self.series != "":
            series = " for series {}".format(self.series)
        if self.channel is not None:
            channel = " from channel {}".format(self.channel)
        return "upload charm {charm}{series}{channel}".format(charm=self.charm,
                                                              series=series,
                                                              channel=channel)


class AddMachineChange(ChangeInfo):
    _toPy = {'series': 'series',
             'constraints': 'constraints',
             'container-type': 'container_type',
             'parent-id': 'parent_id'}

    """AddMachineChange holds a change for adding a machine or container.

    :change_id: id of the change that will be used to identify the current
        change
    :requires: is a slice of dependencies that are required to happen.
    :params: holds the change parameters from the api response. Currently the
        params could either be a list or a dict. The later being the newer
        return results.

    Params holds the following values:
        :series: optional machine OS series.
        :constraints: optional machine constraints.
        :container_type: optionally type of the container (for instance
            "lxc" or kvm"). It is not specified for top level machines.
        :parent_id: id of the parent machine.
    """
    def __init__(self, change_id, requires, params=None):
        super(AddMachineChange, self).__init__(change_id, requires)
        # this one is weird, as it returns a set of parameters inside a list.
        if isinstance(params, list):
            options = params[0] or {}
            self.series = options.get("series")
            self.constraints = options.get("constraints")
            self.container_type = options.get("containerType")
            self.parent_id = options.get("parentId")
        elif isinstance(params, dict):
            AddMachineChange.from_dict(self, params)
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        """method returns an associated ID for the Juju API call.
        """
        return "addMachines"

    async def run(self, context):
        """Executes a AddMachineChange using the returned parameters from
        the API server.

        :param context: is used for any methods or properties required to
            perform a change.
        """
        # Fix up values, as necessary.
        params = {}
        if self.parent_id is not None:
            if self.parent_id.startswith('$addUnit'):
                unit = context.resolve(self.parent_id)[0]
                params['parent_id'] = unit.machine.entity_id
            else:
                params['parent_id'] = context.resolve(self.parent_id)

        params['constraints'] = parse_constraints(self.constraints)
        params['jobs'] = params.get('jobs', ['JobHostUnits'])
        params['series'] = self.series

        if self.container_type == 'lxc':
            log.warning('Juju 2.0 does not support lxc containers. '
                        'Converting containers to lxd.')
            params['container_type'] = 'lxd'
        else:
            params['container_type'] = self.container_type

        # Submit the request.
        params = client.AddMachineParams(**params)
        results = await context.client_facade.AddMachines(params=[params])
        error = results.machines[0].error
        if error:
            raise ValueError("Error adding machine: %s" % error.message)
        machine = results.machines[0].machine
        log.debug('Added new machine %s', machine)
        return machine

    def __str__(self):
        machine = "new machine"
        if self.container_type is not None and self.container_type != "":
            machine = "{container_type} container on {machine}".format(container_type=self.container_type,
                                                                       machine=machine)
        return "add {}".format(machine)


class AddRelationChange(ChangeInfo):
    _toPy = {'endpoint1': 'endpoint1',
             'endpoint2': 'endpoint2'}
    """AddRelationChange holds a change for adding a relation between two
    applications.

    :change_id: id of the change that will be used to identify the current
        change
    :requires: is a slice of dependencies that are required to happen.
    :params: holds the change parameters from the api response. Currently the
        params could either be a list or a dict. The later being the newer
        return results.

    Params holds the following values:
        Endpoint1 and Endpoint2 hold relation endpoints in the
        "application:interface" form, where the application is either a
        placeholder pointing to an application change or in the case of a model
        that already has this application deployed, the name of the
        application, and the interface is optional. Examples are
        "$deploy-42:web", "$deploy-42", "mysql:db".
    """
    def __init__(self, change_id, requires, params=None):
        super(AddRelationChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.endpoint1 = params[0]
            self.endpoint2 = params[1]
        elif isinstance(params, dict):
            AddRelationChange.from_dict(self, params)
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        """method returns an associated ID for the Juju API call.
        """
        return "addRelation"

    async def run(self, context):
        """Executes a AddRelationChange using the returned parameters from
        the API server.

        :param context: is used for any methods or properties required to
            perform a change.
        """
        ep1 = context.resolveRelation(self.endpoint1)
        ep2 = context.resolveRelation(self.endpoint2)

        log.info('Relating %s <-> %s', ep1, ep2)
        return await context.model.add_relation(ep1, ep2)

    def __str__(self):
        return "add relation {endpoint1} - {endpoint2}".format(endpoint1=self.endpoint1,
                                                               endpoint2=self.endpoint2)


class AddUnitChange(ChangeInfo):
    _toPy = {'application': 'application',
             'to': 'to'}
    """AddUnitChange holds a change for adding an application unit.

    :change_id: id of the change that will be used to identify the current
        change
    :requires: is a slice of dependencies that are required to happen.
    :params: holds the change parameters from the api response. Currently the
        params could either be a list or a dict. The later being the newer
        return results.

    Params holds the following values:
        :application: application placeholder name for which a unit is
            added.
        :to: optional location where to add the unit, as a placeholder
            pointing to another unit change or to a machine change.
    """
    def __init__(self, change_id, requires, params=None):
        super(AddUnitChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.application = params[0]
            self.to = params[1]
        elif isinstance(params, dict):
            AddUnitChange.from_dict(self, params)
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        """method returns an associated ID for the Juju API call.
        """
        return "addUnit"

    async def run(self, context):
        """Executes a AddUnitChange using the returned parameters from
        the API server.

        :param context: is used for any methods or properties required to
            perform a change.
        """
        application = context.resolve(self.application)
        placement = context.resolve(self.to)
        if context._units_by_app.get(application):
            # enough units for this application already exist;
            # claim one, and carry on
            # NB: this should probably honor placement, but the juju client
            # doesn't, so we're not bothering, either
            unit_name = context._units_by_app[application].pop()
            log.debug('Reusing unit %s for %s', unit_name, application)
            return context.model.units[unit_name]

        log.debug('Adding new unit for %s%s', application,
                  ' to %s' % placement if placement else '')
        return await context.model.applications[application].add_unit(
            count=1,
            to=placement,
        )

    def __str__(self):
        return "add {application} unit to {to}".format(application=self.application,
                                                       to=self.to)


class CreateOfferChange(ChangeInfo):
    _toPy = {'application': 'application',
             'endpoints': 'endpoints',
             'offer-name': 'offer_name'}
    """CreateOfferChange holds a change for creating a new application endpoint
    offer.

    :change_id: id of the change that will be used to identify the current
        change
    :requires: is a slice of dependencies that are required to happen.
    :params: holds the change parameters from the api response. Currently the
        params could either be a list or a dict. The later being the newer
        return results.

    Params holds the following values:
        :application: is the name of the application to create an offer for.
            added.
        :endpoint: is a list of application endpoint to expose as part of an
            offer.
        :offer_name: describes the offer name.
    """
    def __init__(self, change_id, requires, params=None):
        super(CreateOfferChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.application = params[0]
            self.endpoints = params[1]
            self.offer_name = params[2]
        elif isinstance(params, dict):
            CreateOfferChange.from_dict(self, params)
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        """method returns an associated ID for the Juju API call.
        """
        return "createOffer"

    async def run(self, context):
        """Executes a CreateOfferChange using the returned parameters from
        the API server.

        :param context: is used for any methods or properties required to
            perform a change.
        """
        application = context.resolve(self.application)
        for ep in self.endpoints:
            await context.model.create_offer(ep, offer_name=self.offer_name, application_name=application)

    def __str__(self):
        endpoints = ""
        if self.endpoints is not None:
            endpoints = ":{}".format(self.endpoints.join(","))
        return "create offer {offer_name} using {application}{endpoints}".format(offer_name=self.offer_name,
                                                                                 application=self.application,
                                                                                 endpoints=endpoints)


class ConsumeOfferChange(ChangeInfo):
    _toPy = {'url': 'url',
             'application-name': 'application_name'}
    """CreateOfferChange holds a change for consuming a offer.

    :change_id: id of the change that will be used to identify the current
        change
    :requires: is a slice of dependencies that are required to happen.
    :params: holds the change parameters from the api response. Currently the
        params could either be a list or a dict. The later being the newer
        return results.

    Params holds the following values:
        :url: contains the location of the offer
        :application_name: describes the application name on offer.
    """
    def __init__(self, change_id, requires, params=None):
        super(ConsumeOfferChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.url = params[0]
            self.application_name = params[1]
        elif isinstance(params, dict):
            ConsumeOfferChange.from_dict(self, params)
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        """method returns an associated ID for the Juju API call.
        """
        return "consumeOffer"

    async def run(self, context):
        """Executes a ConsumeOfferChange using the returned parameters from
        the API server.

        :param context: is used for any methods or properties required to
            perform a change.
        """
        application = context.resolve(self.application_name)
        local_name = await context.model.consume(self.url, application_alias=application)
        return local_name

    def __str__(self):
        return "consume offer {application_name} at {url}".format(application_name=self.application_name,
                                                                  url=self.url)


class ExposeChange(ChangeInfo):
    _toPy = {'application': 'application'}
    """ExposeChange holds a change for exposing an application.

    :change_id: id of the change that will be used to identify the current
        change
    :requires: is a slice of dependencies that are required to happen.
    :params: holds the change parameters from the api response. Currently the
        params could either be a list or a dict. The later being the newer
        return results.

    Params holds the following values:
        :application: placeholder name of the application that must be
            exposed.
    """
    def __init__(self, change_id, requires, params=None):
        super(ExposeChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.application = params[0]
        elif isinstance(params, dict):
            ExposeChange.from_dict(self, params)
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        """method returns an associated ID for the Juju API call.
        """
        return "expose"

    async def run(self, context):
        """Executes a ExposeChange using the returned parameters from
        the API server.

        :param context: is used for any methods or properties required to
            perform a change.
        """
        application = context.resolve(self.application)
        log.info('Exposing %s', application)
        return await context.model.applications[application].expose()

    def __str__(self):
        return "expose {application}".format(application=self.application)


class ScaleChange(ChangeInfo):
    _toPy = {'application': 'application',
             'scale': 'scale'}
    """
    ScaleChange holds a change for scaling an application.

    :change_id: id of the change that will be used to identify the current
        change
    :requires: is a slice of dependencies that are required to happen.
    :params: holds the change parameters from the api response. Currently the
        params could either be a list or a dict. The later being the newer
        return results.

    Params holds the following values:
        :application: placeholder name of the application to be scaled.
        :scale: is the new scale value to use.
    """
    def __init__(self, change_id, requires, params=None):
        super(ScaleChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.application = params[0]
            self.scale = params[1]
        elif isinstance(params, dict):
            ScaleChange.from_dict(self, params)
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        """method returns an associated ID for the Juju API call.
        """
        return "scale"

    async def run(self, context):
        """Executes a ScaleChange using the returned parameters from
        the API server.

        :param context: is used for any methods or properties required to
            perform a change.
        """
        application = context.resolve(self.application)
        return await context.model.applications[application].scale(scale=self.scale)

    def __str__(self):
        return "scale {application} to {scale} units".format(application=self.application,
                                                             scale=self.scale)


class SetAnnotationsChange(ChangeInfo):
    _toPy = {'id': 'id',
             'entity-type': 'entity_type',
             'annotations': 'annotations'}
    """SetAnnotationsChange holds a change for setting application and machine
    annotations.

    :change_id: id of the change that will be used to identify the current
        change
    :requires: is a slice of dependencies that are required to happen.
    :params: holds the change parameters from the api response. Currently the
        params could either be a list or a dict. The later being the newer
        return results.

    Params holds the following values:
        :id: is the placeholder for the application or machine change
            corresponding to the entity to be annotated.
        :entity_type: type of the entity, "application" or "machine".
        :ennotations: annotations as key/value pairs.
    """
    def __init__(self, change_id, requires, params=None):
        super(SetAnnotationsChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.id = params[0]
            self.entity_type = params[1]
            self.annotations = params[2]
        elif isinstance(params, dict):
            SetAnnotationsChange.from_dict(self, params)
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        """method returns an associated ID for the Juju API call.
        """
        return "setAnnotations"

    async def run(self, context):
        """Executes a SetAnnotationsChange using the returned parameters from
        the API server.

        :param context: is used for any methods or properties required to
            perform a change.
        """
        entity_id = context.resolve(self.id)
        try:
            entity = context.model.state.get_entity(self.entity_type, entity_id)
        except KeyError:
            entity = await context.model._wait_for_new(self.entity_type, entity_id)
        return await entity.set_annotations(self.annotations)

    def __str__(self):
        return "set annotations for {id}".format(id=self.id)
