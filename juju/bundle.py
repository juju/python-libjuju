import logging
import io
import os
import zipfile
import requests
import base64
from contextlib import closing
from pathlib import Path

import yaml

from toposort import toposort_flatten

from .client import client
from .constraints import parse as parse_constraints, parse_storage_constraint, parse_device_constraint
from .errors import JujuError
from . import utils, jasyncio
from .origin import Channel
from .url import Schema, URL

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
        self.bundle = None
        self.overlays = []
        self.overlay_removed_charms = set()

        self.charmstore = model.charmstore
        self.plan = []
        self.references = {}
        self._units_by_app = {}
        self.origins = {}

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
        self.machine_manager_facade = client.MachineManagerFacade.from_connection(
            model.connection())

        # Feature detect if we have the new charms facade, otherwise fallback
        # to the client facade, when making calls.
        best_facade_version = client.CharmsFacade.best_facade_version(model.connection())
        if best_facade_version is not None and best_facade_version > 2:
            self.charms_facade = client.CharmsFacade.from_connection(
                model.connection())
        else:
            self.charms_facade = None

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
        apps_dict = bundle.get('applications', {})
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

    async def _handle_local_charms(self, bundle, bundle_dir):
        """Search for references to local charms (i.e. filesystem paths)
        in the bundle. Upload the local charms to the model, and replace
        the filesystem paths with appropriate 'local:' paths in the bundle.

        Return the modified bundle.

        :param dict bundle: Bundle dictionary
        :return: Modified bundle dictionary

        """
        apps, args = [], []

        default_series = bundle.get('series')
        apps_dict = bundle.get('applications', {})
        for app_name in self.applications:
            app_dict = apps_dict[app_name]
            charm_dir = app_dict['charm']
            try:
                charm_path = (bundle_dir / charm_dir).resolve()
                if not (charm_path.is_dir() or
                        (charm_path.is_file() and
                         charm_path.suffix in ('.charm', '.zip'))):
                    continue
                charm_dir = str(charm_path)
            except ValueError:
                pass
            except FileNotFoundError:
                continue
            series = (
                app_dict.get('series') or
                default_series or
                await get_charm_series(charm_dir, self.model)
            )
            if not self.model.connection().is_using_old_client and not series:
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
            charm_urls = await jasyncio.gather(*[
                self.model.add_local_charm_dir(*params)
                for params in args
            ])

            # Update the 'charm:' entry for each app with the new 'local:' url.
            for app_name, charm_url, (charm_dir, series) in zip(apps, charm_urls, args):
                metadata = utils.get_local_charm_metadata(charm_dir)
                resources = await self.model.add_local_resources(
                    app_name,
                    charm_url,
                    metadata,
                    resources=bundle.get('applications', {app_name: {}})[app_name].get("resources", {}),
                )
                apps_dict[app_name]['charm'] = charm_url
                apps_dict[app_name]["resources"] = resources
                origin = client.CharmOrigin(source="local", risk="stable")
                if not self.model.connection().is_using_old_client:
                    origin.base = utils.get_local_charm_base(series, '',
                                                             metadata,
                                                             charm_dir,
                                                             client.Base)
                self.origins[charm_url] = {str(None): origin}

        return bundle

    def _resolve_include_file_config(self, bundle_dir):
        """if any of the applications (including the ones in the overlays)
        have "config: include-file:..." or "config:
        include-base64:...", then we have to resolve and inline them
        into the bundle here because they're all files with local
        relative paths, so backend can't handle them.

        """
        bundle_apps = [self.bundle.get('applications', {})]
        overlay_apps = [overlay.get('applications', {}) for overlay in self.overlays]

        for apps in bundle_apps + overlay_apps:
            for app_name, app in apps.items():

                if app and 'options' in app:
                    if 'config' in app['options'] and app['options']['config'].startswith('include-file'):
                        # resolve the file
                        if not bundle_dir:
                            raise NotImplementedError('unable to resolve paths for config:include-file for non-local charms')
                        try:
                            config_path = (bundle_dir / Path(app['options']['config'].split('//')[1])).resolve()
                        except IndexError:
                            raise JujuError('the path for the included file should start with // and be relative to the bundle')
                        if not config_path.exists():
                            raise JujuError('unable to locate config file : %s for : %s' % (config_path, app_name))

                        # get the contents of the file
                        config_contents = yaml.safe_load(config_path.read_text())

                        # inline the configurations for the current app into
                        # the app['options']
                        for key, val in config_contents[app_name].items():
                            app['options'][key] = val

                        # remove the 'include-file' config
                        app['options'].pop('config')

                    for option_key, option_val in app['options'].items():
                        if isinstance(option_val, str) and option_val.startswith('include-base64'):
                            # resolve the file
                            if not bundle_dir:
                                raise NotImplementedError('unable to resolve paths for config:include-base64 for non-local charms')
                            try:
                                base64_path = (bundle_dir / Path(option_val.split('//')[1])).resolve()
                            except IndexError:
                                raise JujuError('the path for the included base64 file should start with // and be relative to the bundle')

                            if not base64_path.exists():
                                raise JujuError('unable to locate the base64 file : %s for : %s' % (base64_path, app_name))

                            # inline the base64 encoded config value
                            base64_contents = base64.b64decode(base64_path.read_text())
                            app['options'][option_key] = base64_contents

        return self.bundle, self.overlays

    async def fetch_plan(self, charm_url, origin, overlays=[]):
        entity_id = charm_url.path()
        is_local = Schema.LOCAL.matches(charm_url.schema)
        bundle_dir = None

        if is_local and os.path.isfile(entity_id):
            bundle_yaml = Path(entity_id).read_text()
            bundle_dir = Path(entity_id).parent
        elif is_local and os.path.isdir(entity_id):
            bundle_yaml = (Path(entity_id) / "bundle.yaml").read_text()
            bundle_dir = Path(entity_id)

        if Schema.CHARM_STORE.matches(charm_url.schema):
            bundle_yaml = await self.charmstore.files(entity_id,
                                                      filename='bundle.yaml',
                                                      read_file=True)
        elif Schema.CHARM_HUB.matches(charm_url.schema):
            bundle_yaml = await self._download_bundle(charm_url, origin)

        if not bundle_yaml:
            raise JujuError('empty bundle, nothing to deploy')

        _bundles = [b for b in yaml.safe_load_all(bundle_yaml)]
        self.overlays = _bundles[1:]
        self.bundle = _bundles[0]

        if overlays != []:
            for overlay_yaml_path in overlays:
                try:
                    overlay_contents = Path(overlay_yaml_path).read_text()
                except (OSError, IOError) as e:
                    raise JujuError('unable to open overlay %s \n %s' % (overlay_yaml_path, e))
                self.overlays.extend(yaml.safe_load_all(overlay_contents))

        # gather the names of the removed charms so model.deploy
        # wouldn't wait for them to appear in the model
        for overlay in self.overlays:
            overlay_apps = overlay.get('applications', {})
            for charm_name, val in overlay_apps.items():
                if val is None:
                    self.overlay_removed_charms.add(charm_name)

        self.bundle = await self._validate_bundle(self.bundle)

        if is_local:
            self.bundle = await self._handle_local_charms(self.bundle, bundle_dir)

        self.bundle, self.overlays = self._resolve_include_file_config(bundle_dir)

        _yaml_data = [yaml.dump(self.bundle)]
        for overlay in self.overlays:
            _yaml_data.append(yaml.dump(overlay).replace('null', ''))
        yaml_data = "---\n".join(_yaml_data)

        self.plan = await self.bundle_facade.GetChanges(
            bundleurl=entity_id,
            yaml=yaml_data)

        if self.plan.errors:
            raise JujuError(self.plan.errors)

    async def _download_bundle(self, charm_url, origin):
        if self.charms_facade is None:
            raise JujuError('unable to download bundle for {} using the new charms facade. Upgrade controller to proceed.'.format(charm_url))

        id = origin.id_ if origin.id_ else ''
        hash = origin.hash_ if origin.hash_ else ''
        charm_origin = {
            'source': origin.source,
            'type': origin.type_,
            'id': id,
            'hash': hash,
            'revision': origin.revision,
            'risk': origin.risk,
            'track': origin.track,
            'architecture': origin.architecture,
        }
        if self.model.connection().is_using_old_client:
            charm_origin['os'] = origin.os
            charm_origin['series'] = origin.series
        else:
            charm_origin['base'] = origin.base

        resp = await self.charms_facade.GetDownloadInfos(entities=[{
            'charm-url': str(charm_url),
            'charm-origin': charm_origin
        }])
        if len(resp.results) != 1:
            raise JujuError("expected one result, received {}".format(resp.results))

        result = resp.results[0]
        if not result.url:
            raise JujuError("no url found for bundle {}".format(charm_url.name))

        bundle_resp = requests.get(result.url)
        bundle_resp.raise_for_status()

        with closing(bundle_resp), zipfile.ZipFile(io.BytesIO(bundle_resp.content)) as archive:
            return self._get_bundle_yaml(archive)

    def _get_bundle_yaml(self, archive):
        for member in archive.infolist():
            if member.filename == "bundle.yaml":
                return archive.read(member)
        raise JujuError("bundle.yaml not found")

    async def _resolve_charms(self):
        deployed = dict()

        specs = self.applications_specs

        for name in self.applications:
            spec = specs[name]
            app = self.model.applications.get(name, None)

            cons = None
            if app is not None:
                deployed[name] = name

                if is_local_charm(spec['charm']):
                    spec['charm'] = self.model.applications[name]
                    continue
                if spec['charm'] == app.charm_url:
                    continue

                cons = await app.get_constraints()

            if is_local_charm(spec['charm']):
                continue

            charm_url = URL.parse(spec['charm'])
            channel = None
            series = spec.get('series', None)
            track, risk = '', ''
            if 'channel' in spec:
                channel = Channel.parse(spec['channel'])
                track, risk = channel.track, channel.risk

                # if not track and series:
                #     track = utils.get_series_version(series)
            if self.charms_facade is not None:
                if cons is not None and cons['arch'] != '':
                    architecture = cons['arch']
                else:
                    architecture = await self.model._resolve_architecture(charm_url)

                origin = client.CharmOrigin(source="charm-hub",
                                            architecture=architecture,
                                            risk=risk,
                                            track=track)
                if not self.model.connection().is_using_old_client and series:
                    origin.base = client.Base(
                        channel=utils.get_series_version(series), name='ubuntu')
                charm_url, charm_origin, _ = await self.model._resolve_charm(charm_url, origin)
                spec['charm'] = str(charm_url)
            else:
                results = await self.model.charmstore.entity(str(charm_url))
                charm_url = results.get('Id', charm_url)
                charm_origin = client.CharmOrigin(source="charm-store",
                                                  risk=risk,
                                                  track=track)

            if str(channel) not in self.origins:
                self.origins[str(charm_url)] = {}
            self.origins[str(charm_url)][str(channel)] = charm_origin

    async def execute_plan(self):
        await self._resolve_charms()

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
        apps_dict = self.bundle.get('applications', {})
        return set(apps_dict.keys()) - self.overlay_removed_charms

    @property
    def applications_specs(self):
        return self.bundle.get('applications', {})

    def resolve_relation(self, reference):
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


def is_local_charm(charm_url):
    return charm_url.startswith('.') or charm_url.startswith('local:') or os.path.isabs(charm_url)


async def get_charm_series(path, model):
    """Inspects the charm directory at ``path`` and returns a default
    series from its metadata.yaml (the first item in the 'series' list).

    Tries to extract the informiation from the given model if no
    series is determined from the path.
    Returns None if no series can be determined.

    """
    path = Path(path)
    try:
        if path.suffix == '.charm':
            md = "metadata.yaml in %s" % path
            with zipfile.ZipFile(str(path), 'r') as charm_file:
                data = yaml.safe_load(charm_file.read('metadata.yaml'))
        else:
            md = path / "metadata.yaml"
            if not md.exists():
                return None
            data = yaml.safe_load(md.open())
    except yaml.YAMLError as exc:
        if hasattr(exc, "problem_mark"):
            mark = exc.problem_mark
            log.error("Error parsing YAML file {}, line {}, column: {}".format(md, mark.line, mark.column))
        raise
    _series = data.get('series')
    series = _series[0] if _series else None

    if series is None:
        # get the ConfigValue for the 'default-series' from the model
        model_config = await model.get_config()
        _default_series = model_config.get("default-series")

        if _default_series is not None:
            # then update the series with its value
            series = _default_series.value

    return series


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
             'num-units': 'num_units',
             'channel': 'channel'}

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
            self.channel = None
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
                if len(params) > 10:
                    self.channel = params[10]

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
        # NB: this should really be handled by the controller when generating the
        # bundle change plan, and this short-term workaround may be missing some
        # aspects of the logic which the CLI client contains to handle edge cases.
        if self.application in context.model.applications:
            log.debug('Skipping %s; already in model', self.application)
            return self.application

        # resolve indirect references
        charm = context.resolve(self.charm)
        options = {}
        if self.options is not None:
            options = self.options
        if context.trusted:
            if context.model.info.agent_version < client.Number.from_json('2.4.0'):
                raise NotImplementedError("trusted is not supported on model version {}".format(context.model.info.agent_version))
            options["trust"] = "true"

        url = URL.parse(str(charm))

        # set the channel to the default value if not specified
        if not self.channel:
            if Schema.CHARM_STORE.matches(url.schema):
                self.channel = "stable"
            elif Schema.CHARM_HUB.matches(url.schema):
                self.channel = "latest/stable"
            else:   # for local charms
                self.channel = ""

        channel = None
        non_normalized_channel = None
        if self.channel is not None and self.channel != "":
            non_normalized_channel = Channel.parse(self.channel)
            channel = non_normalized_channel.normalize()

        origin = context.origins.get(str(url), {}).get(
            str(channel),
            context.origins.get(str(url), {}).get(str(non_normalized_channel), None),
        )
        if origin is None:
            raise JujuError("expected origin to be valid for application {} and charm {} with channel {}".format(self.application, str(url), str(channel)))

        if self.series is None or self.series == "":
            self.series = context.bundle.get("series", None)

        if Schema.CHARM_STORE.matches(url.schema):
            resources = await context.model._add_store_resources(
                self.application, charm, overrides=self.resources)
        elif Schema.CHARM_HUB.matches(url.schema):
            resources = await context.model._add_charmhub_resources(
                self.application, charm, origin, overrides=self.resources)
        else:
            resources = context.bundle.get("applications", {}).get(self.application, {}).get("resources", {})

        await context.model._deploy(
            charm_url=charm,
            application=self.application,
            series=self.series,
            config=options,
            constraints=self.constraints,
            endpoint_bindings=self.endpoint_bindings,
            resources=resources,
            storage=self.storage,
            channel=self.channel,
            devices=self.devices,
            num_units=self.num_units,
            charm_origin=origin,
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
             'channel': 'channel',
             'architecture': 'architecture'}

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
            if len(params) > 3 and params[3] != "":
                self.architecture = params[3]
            else:
                self.architecture = None
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
        url = URL.parse(str(self.charm))
        ch = None
        identifier = None
        if Schema.LOCAL.matches(url.schema):
            return self.charm

        if Schema.CHARM_STORE.matches(url.schema):
            entity_id = await context.charmstore.entityId(self.charm, channel=self.channel)
            log.debug('Adding %s', entity_id)
            await context.charms_facade.AddCharm(channel=self.channel, url=entity_id, force=False)
            identifier = entity_id
            origin = client.CharmOrigin(source="charm-store", risk="stable")

        if Schema.CHARM_HUB.matches(url.schema):
            ch = Channel('latest', 'stable')
            if self.channel:
                ch = Channel.parse(self.channel).normalize()
            arch = self.architecture
            if not arch:
                arch = await context.model._resolve_architecture(url)
            origin = client.CharmOrigin(source="charm-hub",
                                        architecture=arch,
                                        risk=ch.risk,
                                        track=ch.track)
            if not context.model.connection().is_using_old_client and self.series:
                origin.base = client.Base(
                    channel=utils.get_series_version(self.series),
                    name='ubuntu')
            identifier, origin, _ = await context.model._resolve_charm(url, origin)

        if identifier is None:
            raise JujuError('unknown charm {}'.format(self.charm))

        await context.model._add_charm(identifier, origin)

        if str(ch) not in context.origins:
            context.origins[str(identifier)] = {}
        context.origins[str(identifier)][str(ch)] = origin

        return str(identifier) if identifier is not None else url.path()

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
        if not context.model.connection().is_using_old_client:
            params['base'] = client.Base(
                channel=utils.get_series_version(self.series),
                name='ubuntu')
        else:
            params['series'] = self.series

        if self.container_type == 'lxc':
            log.warning('Juju 2.0 does not support lxc containers. '
                        'Converting containers to lxd.')
            params['container_type'] = 'lxd'
        else:
            params['container_type'] = self.container_type

        # Submit the request.
        params = client.AddMachineParams(**params)
        results = await context.machine_manager_facade.AddMachines(params=[params])
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
        ep1 = context.resolve_relation(self.endpoint1)
        ep2 = context.resolve_relation(self.endpoint2)

        # NB: this should really be handled by the controller when generating the
        # bundle change plan, and this short-term workaround may be missing some
        # aspects of the logic which the CLI client contains to handle edge cases.
        existing = [rel for rel in context.model.relations if rel.matches(ep1, ep2)]
        if existing:
            log.info('Skipping %s <-> %s; already related', ep1, ep2)
            return existing[0]

        log.info('Relating %s <-> %s', ep1, ep2)
        return await context.model.relate(ep1, ep2)

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
    _toPy = {
        'application': 'application',
        'exposed-endpoints': 'exposed_endpoints',
    }
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
        :exposed_endpoints: a an optional dictionary where keys are endpoint
            names and values are dicts that specify the space names and CIDRs
            that should be able to access the port ranges that the application
            has opened for each endpoint.
    """
    def __init__(self, change_id, requires, params=None):
        super(ExposeChange, self).__init__(change_id, requires)

        self.exposed_endpoints = None
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
        return await context.model.applications[application].expose(self.exposed_endpoints)

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
