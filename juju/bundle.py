import asyncio
import logging
import os
from pathlib import Path

import yaml

from toposort import toposort_flatten

from .client import client
from .constraints import parse as parse_constraints
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
            # Explicitly call out what methods we work with, so it makes it
            # very easy to understand what happens with the execution.
            change = change_cls(step.id_, step.requires, step.args)
            log.info(change.description())
            if step.method == AddApplicationChange.method():
                result = await self.handleAddApplication(change)
            elif step.method == AddCharmChange.method():
                result = await self.handleAddCharm(change)
            elif step.method == AddMachineChange.method():
                result = await self.handleAddMachine(change)
            elif step.method == AddRelationChange.method():
                result = await self.handleAddRelation(change)
            elif step.method == AddUnitChange.method():
                result = await self.handleAddUnit(change)
            elif step.method == CreateOfferChange.method():
                result = await self.handleCreateOffer(change)
            elif step.method == ConsumeOfferChange.method():
                result = await self.handleConsumeOffer(change)
            elif step.method == ExposeChange.method():
                result = await self.handleExpose(change)
            elif step.method == ScaleChange.method():
                result = await self.handleScale(change)
            elif step.method == SetAnnotationsChange.method():
                result = await self.handleSetAnnotations(change)
            else:
                raise NotImplementedError("unknown change type: {}".format(step.method))
            self.references[step.id_] = result

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

    async def handleAddApplication(self, change):
        """
        :param change AddApplicationChange: holds a change for deploying a Juju
            application.
        """
        # resolve indirect references
        charm = self.resolve(change.charm)
        options = {}
        if change.options is not None:
            options = change.options
        if self.trusted:
            if self.model.info.agent_version < client.Number.from_json('2.4.0'):
                raise NotImplementedError("trusted is not supported on model version {}".format(self.model.info.agent_version))
            options["trust"] = "true"
        if not charm.startswith('local:'):
            resources = await self.model._add_store_resources(
                change.application, charm, overrides=change.resources)
        await self.model._deploy(
            charm_url=charm,
            application=change.application,
            series=change.series,
            config=change.options,
            constraints=change.constraints,
            endpoint_bindings=change.endpoint_bindings,
            resources=resources,
            storage=change.storage,
            devices=change.devices,
            num_units=change.num_units,
        )
        return change.application

    async def handleAddCharm(self, change):
        """
        :param change AddCharmChange: change holds the charm changes when
            deploying a charm.
        """
        # We don't add local charms because they've already been added
        # by self._handle_local_charms
        if change.charm.startswith('local:'):
            return change.charm

        entity_id = await self.charmstore.entityId(change.charm)
        log.debug('Adding %s', entity_id)
        await self.client_facade.AddCharm(channel=None, url=entity_id, force=False)
        return entity_id

    async def handleAddMachine(self, change):
        """
        :param change AddMachineChange: holds a change for adding a machine or
            container.
        """
        # Fix up values, as necessary.
        params = {}
        if change.parent_id is not None:
            if params['parent_id'].startswith('$addUnit'):
                unit = self.resolve(params['parent_id'])[0]
                params['parent_id'] = unit.machine.entity_id
            else:
                params['parent_id'] = self.resolve(params['parent_id'])

        params['constraints'] = parse_constraints(change.constraints)
        params['jobs'] = params.get('jobs', ['JobHostUnits'])

        if change.container_type == 'lxc':
            log.warning('Juju 2.0 does not support lxc containers. '
                        'Converting containers to lxd.')
            params['container_type'] = 'lxd'

        # Submit the request.
        params = client.AddMachineParams(**params)
        results = await self.client_facade.AddMachines(params=[params])
        error = results.machines[0].error
        if error:
            raise ValueError("Error adding machine: %s" % error.message)
        machine = results.machines[0].machine
        log.debug('Added new machine %s', machine)
        return machine

    async def handleAddUnit(self, change):
        """
        :param change AddUnitChange: holds a change for adding an application
            unit.
        """
        application = self.resolve(change.application)
        placement = self.resolve(change.to)
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

    async def handleAddRelation(self, change):
        """
        :param change AddRelationChange: change holds the relation changes when
            adding a relation.
        """
        ep1 = self.resolveRelation(change.endpoint1)
        ep2 = self.resolveRelation(change.endpoint2)

        log.info('Relating %s <-> %s', ep1, ep2)
        return await self.model.add_relation(ep1, ep2)

    async def handleCreateOffer(self, change):
        """
        :param change CreateOfferChange: holds a change for creating a new
            application endpoint offer.
        """
        application = self.resolve(change.application_name)
        for ep in change.endpoints:
            await self.model.create_offer(ep, offer_name=change.offer_name, application_name=application)

    async def handleConsumeOffer(self, change):
        """
        :param change ConsumeOfferChange: holds a change for consuming a offer.
        """
        application = self.resolve(change.application_name)
        local_name = await self.model.consume(change.url, application_alias=application)
        return local_name

    async def handleExpose(self, change):
        """
        :param change ExposeChange: holds a change for exposing an application.
        """
        application = self.resolve(change.application)
        log.info('Exposing %s', application)
        return await self.model.applications[application].expose()

    async def handleScale(self, change):
        """
        :param change ScaleChange: change holds the scale for a k8s application.
        """
        application = self.resolve(change.application)
        return await self.model.applications[application].scale(scale=change.scale)

    async def handleSetAnnotations(self, change):
        """
        :param change SetAnnotationsChange: holds a change for setting
            application and machine annotations.
        """
        entity_id = self.resolve(change.id)
        try:
            entity = self.model.state.get_entity(change.entity_type, entity_id)
        except KeyError:
            entity = await self.model._wait_for_new(change.entity_type, entity_id)
        return await entity.set_annotations(change.annotations)


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

    def __init__(self, change_id, requires):
        self.change_id = change_id
        self.requires = requires


class AddApplicationChange(ChangeInfo):
    """
    AddCharmChange holds a change for deploying a Juju application.

    :charm: holds the URL of the charm to be used to deploy this application.
    :series: holds the series of the application to be deployed if the charm
        default is not sufficient.
    :application: holds the application name.
    :num_units: holds the number of units required. For IAAS models, this will
        be 0 and separate AddUnitChanges will be used. For Kubernetes models,
        this will be used to scale the application.
    :options: holds application options.
    :constraints: holds the optional application constraints.
    :storage: holds the optional storage constraints.
    :devices: holds the optional devices constraints.
    :endpoint_bindings: holds the optional endpoint bindings
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
            self.storage = params[5]
            self.endpoint_bindings = params[6]
            if len(params) == 8:
                # Juju 2.4 and below only sends the resources
                self.resources = params[7]
                self.devices = None
                self.num_units = None
            else:
                # Juju 2.5+ sends devices before resources, as well as num_units
                # There might be placement but we need to ignore that.
                self.devices = params[7]
                self.resources = params[8]
                self.num_units = params[9]

        elif isinstance(params, dict):
            self.charm = params["charm"]
            self.series = params["series"]
            self.application = params["application"]
            self.options = params["options"]
            self.constraints = params["constraints"]
            self.storage = params["storage"]
            self.devices = params["devices"]
            self.endpoint_bindings = params["endpoint-bindings"]
            self.resources = params["resources"]
            self.num_units = params["num-units"]
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        return "deploy"

    def description(self):
        series = ""
        if self.series != "":
            series = " on {}".format(self.series)
        units_info = ""
        if self.num_units > 0:
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
    """
    AddCharmChange holds a change for adding a charm to the environment.

    :charm: holds the URL of the charm to be added.
    :series: holds the series of the charm to be added if the charm default is
        not sufficient.
    :channel: holds the preferred channel for obtaining the charm.
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
            self.charm = params["charm"]
            self.series = params["series"]
            if "channel" in params and params["channel"] != "":
                self.channel = params["channel"]
            else:
                self.channel = None
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        return "addCharm"

    def description(self):
        series = ""
        channel = ""
        if self.series != "":
            series = " for series {}".format(self.series)
        if self.channel is not None:
            channel = " from channel {}".format(self.channel)
        return "upload charm {charm}{series}{channel}".format(charm=self.charm,
                                                              series=series,
                                                              channel=channel)


class AddMachineChange(ChangeInfo):
    """
    AddMachineChange holds a change for adding a machine or container.

    :series: holds the optional machine OS series.
    :constraints: holds the optional machine constraints.
    :container_type: optionally holds the type of the container (for instance
        "lxc" or kvm"). It is not specified for top level machines.
    :parent_id: holds the id of the parent machine.
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
            self.series = params["series"]
            self.constraints = params["constraints"]
            self.container_type = params["container-type"]
            self.parent_id = params["parent-id"]
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        return "addMachines"

    def description(self):
        machine = "new machine"
        if self.container_type is not None and self.container_type != "":
            machine = "{container_type} container on {machine}".format(container_type=self.container_type,
                                                                       machine=machine)
        return "add {}".format(machine)


class AddRelationChange(ChangeInfo):
    """
    AddRelationChange holds a change for adding a relation between two
    applications.

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
            self.endpoint1 = params["endpoint1"]
            self.endpoint2 = params["endpoint2"]
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        return "addRelation"

    def description(self):
        return "add relation {endpoint1} - {endpoint2}".format(endpoint1=self.endpoint1,
                                                               endpoint2=self.endpoint2)


class AddUnitChange(ChangeInfo):
    """
    AddUnitChange holds a change for adding an application unit.

    :application: holds the application placeholder name for which a unit is
        added.
    :to: holds the optional location where to add the unit, as a placeholder
        pointing to another unit change or to a machine change.
    """
    def __init__(self, change_id, requires, params=None):
        super(AddUnitChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.application = params[0]
            self.to = params[1]
        elif isinstance(params, dict):
            self.application = params["application"]
            self.to = params["to"]
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        return "addUnit"

    def description(self):
        return "add {application} unit to {to}".format(application=self.application,
                                                       to=self.to)


class CreateOfferChange(ChangeInfo):
    """
    CreateOfferChange holds a change for creating a new application endpoint
    offer.

    :application: is the name of the application to create an offer for.
        added.
    :endpoint: is a list of application endpoint to expose as part of an offer.
    :offer_name: describes the offer name.
    """
    def __init__(self, change_id, requires, params=None):
        super(CreateOfferChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.application = params[0]
            self.endpoints = params[1]
            self.offer_name = params[2]
        elif isinstance(params, dict):
            self.application = params["application"]
            self.endpoints = params["endpoints"]
            self.offer_name = params["offer-name"]
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        return "createOffer"

    def description(self):
        return "create offer {offer_name} using {application}:{endpoints}".format(offer_name=self.offer_name,
                                                                                  application=self.application,
                                                                                  endpoints=self.endpoints.join(","))


class ConsumeOfferChange(ChangeInfo):
    """
    CreateOfferChange holds a change for consuming a offer.

    :url: contains the location of the offer
    :application_name: describes the application name on offer.
    """
    def __init__(self, change_id, requires, params=None):
        super(ConsumeOfferChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.url = params[0]
            self.application_name = params[1]
        elif isinstance(params, dict):
            self.url = params["url"]
            self.application_name = params["application_name"]
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        return "consumeOffer"

    def description(self):
        return "consume offer {application_name} at {url}".format(application_name=self.application_name,
                                                                  url=self.url)


class ExposeChange(ChangeInfo):
    """
    ExposeChange holds a change for exposing an application.

    :application: holds the placeholder name of the application that must be
        exposed.
    """
    def __init__(self, change_id, requires, params=None):
        super(ExposeChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.application = params[0]
        elif isinstance(params, dict):
            self.application = params["application"]
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        return "expose"

    def description(self):
        return "expose {application}".format(application=self.application)


class ScaleChange(ChangeInfo):
    """
    ScaleChange holds a change for scaling an application.

    :application: holds the placeholder name of the application to be scaled.
    :scale: is the new scale value to use.
    """
    def __init__(self, change_id, requires, params=None):
        super(ScaleChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.application = params[0]
            self.scale = params[1]
        elif isinstance(params, dict):
            self.application = params["application"]
            self.scale = params["scale"]
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        return "scale"

    def description(self):
        return "scale {application} to {scale} units".format(application=self.application,
                                                             scale=self.scale)


class SetAnnotationsChange(ChangeInfo):
    """
    SetAnnotationsChange holds a change for setting application and machine
    annotations.

    :id: is the placeholder for the application or machine change corresponding
        to the entity to be annotated.
    :entity_type: holds the type of the entity, "application" or "machine".
    :ennotations: holds the annotations as key/value pairs.
    """
    def __init__(self, change_id, requires, params=None):
        super(SetAnnotationsChange, self).__init__(change_id, requires)

        if isinstance(params, list):
            self.id = params[0]
            self.entity_type = params[1]
            self.annotations = params[2]
        elif isinstance(params, dict):
            self.id = params["id"]
            self.entity_type = params["entity-type"]
            self.annotations = params["annotations"]
        else:
            raise Exception("unexpected params type")

    @staticmethod
    def method():
        return "setAnnotations"

    def description(self):
        return "set annotations for {id}".format(id=self.id)
