import asyncio
import logging
import os
from pathlib import Path

import yaml

from toposort import toposort_flatten

from .client import client
from .constraints import normalize_key
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
        client.BundleChange.__repr__ = lambda self: "BundleChange({}, {})".format(self.id_, self.requires)
        changes = ChangeSet(self.plan.changes)
        for step in changes.sorted():
            method = getattr(self, step.method)
            result = await method(step.id_, *step.args)
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

    async def addCharm(self, change_id, charm, series):
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
        await self.client_facade.AddCharm(channel=None, url=entity_id, force=False)
        return entity_id

    async def addMachines(self, change_id, params=None):
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
            if params['parent_id'].startswith('$addUnit'):
                unit = self.resolve(params['parent_id'])[0]
                params['parent_id'] = unit.machine.entity_id
            else:
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
        results = await self.client_facade.AddMachines(params=[params])
        error = results.machines[0].error
        if error:
            raise ValueError("Error adding machine: %s" % error.message)
        machine = results.machines[0].machine
        log.debug('Added new machine %s', machine)
        return machine

    async def addRelation(self, change_id, endpoint1, endpoint2):
        """
        :param endpoint1 string:
        :param endpoint2 string:
            Endpoint1 and Endpoint2 hold relation endpoints in the
            "application:interface" form, where the application is always a
            placeholder pointing to an application change, and the interface is
            optional. Examples are "$deploy-42:web" or just "$deploy-42".
        """
        ep1 = self.resolveRelation(endpoint1)
        ep2 = self.resolveRelation(endpoint2)

        log.info('Relating %s <-> %s', ep1, ep2)
        return await self.model.add_relation(ep1, ep2)

    async def deploy(self, change_id, charm, series, application, options, constraints,
                     storage, endpoint_bindings, *args):
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

        :param devices map[string]string:
            Devices holds the optional devices constraints.
            (Only given on Juju 2.5+)

        :param resources map[string]int:
            Resources identifies the revision to use for each resource
            of the application's charm.

        :param num_units int:
            NumUnits holds the number of units required.  For IAAS models, this
            will be 0 and separate AddUnitChanges will be used.  For Kubernetes
            models, this will be used to scale the application.
            (Only given on Juju 2.5+)
        """
        # resolve indirect references
        charm = self.resolve(charm)

        if len(args) == 1:
            # Juju 2.4 and below only sends the resources
            resources = args[0]
            devices, num_units = None, None
        else:
            # Juju 2.5+ sends devices before resources, as well as num_units
            # There might be placement but we need to ignore that.
            devices, resources, num_units = args[:3]

        if options is None:
            options = {}
        if self.trusted:
            if self.model.info.agent_version < client.Number.from_json('2.4.0'):
                raise NotImplementedError("trusted is not supported on model version {}".format(self.model.info.agent_version))
            options["trust"] = "true"
        if not charm.startswith('local:'):
            resources = await self.model._add_store_resources(
                application, charm, overrides=resources)
        await self.model._deploy(
            charm_url=charm,
            application=application,
            series=series,
            config=options,
            constraints=constraints,
            endpoint_bindings=endpoint_bindings,
            resources=resources,
            storage=storage,
            devices=devices,
            num_units=num_units,
        )
        return application

    async def addUnit(self, change_id, application, to):
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

    async def scale(self, change_id, application, scale):
        """
        Handle a change of scale to a k8s application.

        :param string application:
            Application holds the application placeholder name for which a unit
            is added.

        :param int scale:
            New scale value to use.
        """
        application = self.resolve(application)
        return await self.model.applications[application].scale(scale=scale)

    async def expose(self, change_id, application):
        """
        :param application string:
            Application holds the placeholder name of the application that must
            be exposed.
        """
        application = self.resolve(application)
        log.info('Exposing %s', application)
        return await self.model.applications[application].expose()

    async def setAnnotations(self, change_id, id_, entity_type, annotations):
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

    async def createOffer(self, change_id, endpoints, application_name, offer_name):
        """
        :param application_name string:
            Application is the name of the application to create an offer for.
        :param endpoints [string]:
            Endpoint is a list of application endpoint to expose as part of an
            offer.
        :param offer_name string:
            OfferName describes the offer name.
        """
        application = self.resolve(application_name)
        for ep in endpoints:
            await self.model.create_offer(ep, offer_name=offer_name, application_name=application)

    async def consumeOffer(self, change_id, url, application_name):
        """
        :param application_name string:
            Application is the name of the application on offer.
        :param url string:
            URL contains the location of the offer
        """
        application = self.resolve(application_name)
        local_name = await self.model.consume(url, application_alias=application)
        return local_name

    async def grantOfferAccess(self, change_id, user, access, offer_name):
        """
        :param user string:
            User holds the user name to grant access to.
        :param access string:
            The type of access to grant.
        :param offer string:
            The offer name to be granted access to.
        """
        raise NotImplementedError()


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
