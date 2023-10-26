# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import hashlib
import json
import logging
from pathlib import Path

from . import model, tag, utils, jasyncio
from .url import URL
from .status import derive_status
from .annotationhelper import _get_annotations, _set_annotations
from .client import client
from .errors import JujuError, JujuApplicationConfigError
from .bundle import get_charm_series, is_local_charm
from .placement import parse as parse_placement
from .origin import Channel, Source

log = logging.getLogger(__name__)


class Application(model.ModelEntity):
    @property
    def _unit_match_pattern(self):
        return r'^{}.*$'.format(self.entity_id)

    def _facade(self):
        return client.ApplicationFacade.from_connection(self.connection)

    def _facade_version(self):
        return client.ApplicationFacade.best_facade_version(self.connection)

    def on_unit_add(self, callable_):
        """Add a "unit added" observer to this entity, which will be called
        whenever a unit is added to this application.

        """
        self.model.add_observer(
            callable_, 'unit', 'add', self._unit_match_pattern)

    def on_unit_remove(self, callable_):
        """Add a "unit removed" observer to this entity, which will be called
        whenever a unit is removed from this application.

        """
        self.model.add_observer(
            callable_, 'unit', 'remove', self._unit_match_pattern)

    @property
    def units(self):
        return [
            unit for unit in self.model.units.values()
            if unit.application == self.name
        ]

    @property
    def subordinate_units(self):
        """Returns the subordinate units of this application"""
        return [u for u in self.units if u.is_subordinate]

    @property
    def relations(self):
        return [rel for rel in self.model.relations if rel.matches(self.name)]

    def related_applications(self, endpoint_name=None):
        apps = {}
        for rel in self.relations:
            if rel.is_peer:
                local_ep, remote_ep = rel.endpoints[0]
            else:
                def is_us(ep):
                    return ep.application.name == self.name
                local_ep, remote_ep = sorted(rel.endpoints, key=is_us)
            if endpoint_name is not None and endpoint_name != local_ep.name:
                continue
            apps[remote_ep.application.name] = remote_ep.application
        return apps

    @property
    def status(self):
        """Get the application status.

        If the application is unknown it will attempt to derive the unit
        workload status and highlight the most relevant (severity).
        """
        status = self.safe_data['status']['current']
        if status == "unset":
            known_statuses = []
            for unit in self.units:
                known_statuses.append(unit.workload_status)
            # If the self.get_status() is called (i.e. the status
            # is received by FullStatus from the API) then add
            # that into this computation as it might be more up
            # to date (and more severe).
            known_statuses.append(self._status)
            return derive_status(known_statuses)
        return status

    @property
    def status_message(self):
        """Get the application status message, as set by the charm's leader.

        """
        return self.safe_data['status']['message']

    @property
    def tag(self):
        return tag.application(self.name)

    async def add_relation(self, local_relation, remote_relation):
        """
        .. deprecated:: 2.9.9
           Use ``relate()`` instead
        """
        return await self.relate(local_relation, remote_relation)

    async def relate(self, local_relation, remote_relation):
        """Add a relation to another application.

        :param str local_relation: Name of relation on this application
        :param str remote_relation: Name of relation on the other
            application in the form '<application>[:<relation_name>]'

        """
        if ':' not in local_relation:
            local_relation = '{}:{}'.format(self.name, local_relation)

        return await self.model.relate(local_relation, remote_relation)

    async def add_unit(self, count=1, to=None, attach_storage=[]):
        """Add one or more units to this application.

        :param int count: Number of units to add
        :param [str] attach_storage: Existing storage to attach to the deployed unit
        (not available on k8s models)
        :param str to: Placement directive, e.g.::
            '23' - machine 23
            'lxc:7' - new lxc container on machine 7
            '24/lxc/3' - lxc container 3 or machine 24

            If None, a new machine is provisioned.

        """

        if self.model.info.type_ == 'caas':
            log.warning('adding units to a container-based model not supported, auto-switching to scale')
            return await self.scale(scale_change=count)

        app_facade = self._facade()

        log.debug(
            'Adding %s unit%s to %s',
            count, '' if count == 1 else 's', self.name)

        result = await app_facade.AddUnits(
            application=self.name,
            placement=parse_placement(to) if to else None,
            num_units=count,
            attach_storage=attach_storage,
        )

        return await jasyncio.gather(*[
            jasyncio.ensure_future(self.model._wait_for_new('unit', unit_id))
            for unit_id in result.units
        ])

    add_units = add_unit

    async def scale(self, scale=None, scale_change=None):
        """
        Set or adjust the scale of this (K8s) application.

        One or the other of scale or scale_change must be provided.

        :param int scale: Scale to which to set this application.
        :param int scale_change: Amount by which to adjust the scale of this
            application (can be positive or negative).
        """
        app_facade = self._facade()

        if (scale, scale_change) == (None, None):
            raise ValueError('Must provide either scale or scale_change')

        log.debug(
            'Scaling application %s %s %s',
            self.name, 'to' if scale else 'by', scale or scale_change)

        await app_facade.ScaleApplications(applications=[
            client.ScaleApplicationParams(application_tag=self.tag,
                                          scale=scale,
                                          scale_change=scale_change)
        ])

    async def destroy_relation(self, local_relation, remote_relation):
        """Remove a relation to another application.

        :param str local_relation: Name of relation on this application
        :param str remote_relation: Name of relation on the other
            application in the form '<application>[:<relation_name>]'

        """
        if ':' not in local_relation:
            local_relation = '{}:{}'.format(self.name, local_relation)

        app_facade = self._facade()

        log.debug(
            'Destroying relation %s <-> %s', local_relation, remote_relation)

        return await app_facade.DestroyRelation(endpoints=[
            local_relation, remote_relation])
    remove_relation = destroy_relation

    async def destroy_unit(self, *unit_names):
        """Destroy units by name.

        """
        return await self.model.destroy_units(*unit_names)
    destroy_units = destroy_unit

    async def destroy(self, destroy_storage=False, force=False, no_wait=False):
        """Remove this application from the model.

        :param bool destroy_storage: Destroy storage attached to application unit. (=false)
        :param bool force: Completely remove an application and all its dependencies. (=false)
        :param bool no_wait: Rush through application removal without waiting for each individual step to complete (=false)
        :param bool block: Blocks until the application is removed from the model
        """

        if no_wait and not force:
            raise JujuError("--no-wait without --force is not valid")

        app_facade = self._facade()

        log.debug('Destroying {} with parameters -- destroy-storage : {} -- force : {} -- no-wait : {}'.format(
            self.name, destroy_storage, force, no_wait))

        res = await app_facade.DestroyApplication(applications=[client.DestroyApplicationParams(
            application_tag=self.tag,
            destroy_storage=destroy_storage,
            force=force,
            max_wait=0 if no_wait else None,
        )])
        return res
    remove = destroy

    def supports_granular_expose_parameters(self):
        """Returns true if the controller supports granular, per-endpoint
           expose parameters."""
        return self._facade_version() >= 13

    async def expose(self, exposed_endpoints=None):
        """Make a subset of the application endpoints or the entire application
           available over the network.

           If the exposed_endpoints argument is not provided, all opened port
           ranges for the application will become reachable from 0.0.0.0/0.

           On juju 2.9 and onwards, the exposed_endpoints argument may be used
           to specify a list of spaces and or CIDRs that should be able to
           reach the port ranges opened for a particular subnet. The
           exposed_endpoints parameter is a map where keys are endpoint names
           or the empty string ("") which works as a wildcard for all endpoints
           and values are ExposedEndpoint instances.

           When targeting an older juju controller, the exposed_endpoints param
           is not supported and an error will be raised if it is provided.
        """
        app_facade = self._facade()
        ctrl_supports_expose_parameters = self.supports_granular_expose_parameters()

        if exposed_endpoints is not None:
            if not isinstance(exposed_endpoints, dict):
                raise ValueError("endpoints must be a dictionary with ExposedEndpoint values")

            # The bundle changes code will pass in raw dicts with the exposed
            # endpoint data. We need to convert those into ExposedEndpoints
            for k, v in exposed_endpoints.items():
                if not isinstance(v, ExposedEndpoint):
                    exposed_endpoints[k] = ExposedEndpoint.from_dict(v)

            # Check if the specified exposed_endpoints would cause security
            # issues when applied to a pre 2.9 controller.
            has_more_than_one_endpoints = len(exposed_endpoints) > 1
            has_non_wildcard_endpoint = (
                len(exposed_endpoints) > 0 and "" not in exposed_endpoints
            )
            has_wildcard_endpoint_with_spaces_or_non_wildcard_cidrs = (
                "" in exposed_endpoints and (
                    exposed_endpoints[""].includes_non_wildcard_cidrs() or
                    exposed_endpoints[""].includes_spaces()
                )
            )

            is_security_risk = (
                not ctrl_supports_expose_parameters and
                (
                    has_more_than_one_endpoints or
                    has_non_wildcard_endpoint or
                    has_wildcard_endpoint_with_spaces_or_non_wildcard_cidrs
                )
            )

            if is_security_risk:
                raise JujuError("controller does not support granular expose parameters; applying this change would make all open application ports accessible from 0.0.0.0/0")

            for endpoint, expose_details in exposed_endpoints.items():
                access_from = "from CIDRs 0.0.0.0/0 and ::/0"
                if isinstance(expose_details, ExposedEndpoint):
                    access_from = str(expose_details)

                if endpoint == "":
                    log.debug("expose all endpoints of %s and allow access %s", self.name, access_from)
                else:
                    log.debug("override expose settings for endpoint %s of %s and %s", endpoint, self.name, access_from)

            # Map ExposedEndpoint entries to a dict we can pass to the facade.
            exposed_endpoints = {
                k: v.to_dict() for k, v in exposed_endpoints.items()
            }
        else:
            log.debug("expose all endpoints of %s and allow access from CIDRs 0.0.0.0/0 and ::/0", self.name)

        if not ctrl_supports_expose_parameters:
            return await app_facade.Expose(application=self.name)

        return await app_facade.Expose(application=self.name,
                                       exposed_endpoints=exposed_endpoints)

    async def unexpose(self, exposed_endpoints=None):
        """Prevent a subset of the application endpoints or the entire
           application from being reached over the network.

           If the exposed_endpoints argument is not provided, the entire
           application will be unexposed.

           On juju 2.9 and onwards, the exposed_endpoints argument may be used
           to specify a list of endpoint names whose port ranges should be
           unexposed.

           When targeting an older juju controller, the exposed_endpoints param
           is not supported and an error will be raised if it is provided.
        """
        app_facade = self._facade()
        facade_version = self._facade_version()

        # Check if an endpoint list is provided
        if exposed_endpoints is not None and len(exposed_endpoints) > 0:
            if facade_version < 13:
                raise JujuError("controller does not support granular expose parameters; applying this change would unexpose the application")

            log.debug("Unexposing endpoints %s of %s", ",".join(exposed_endpoints), self.name)
            return await app_facade.Unexpose(application=self.name,
                                             exposed_endpoints=exposed_endpoints)

        # Just expose the entire application
        log.debug("Unexposing %s", self.name)
        return await app_facade.Unexpose(application=self.name)

    async def get_series(self):
        """Return the series on which the application is deployed

        :return: str series
        """
        app_facade = self._facade()

        log.debug(
            'Getting series for %s', self.name)

        appGetResults = (await app_facade.Get(application=self.name))
        if self._facade_version() >= 15:
            base_channel = appGetResults.base.channel
            return utils.base_channel_to_series(base_channel)
        return appGetResults.series

    async def get_config(self):
        """Return the configuration settings dict for this application.
        """
        app_facade = self._facade()

        log.debug(
            'Getting config for %s', self.name)

        return (await app_facade.Get(application=self.name)).config

    async def get_trusted(self):
        """Return the trusted configuration setting for this application.

        """
        if self.model.info.agent_version < client.Number.from_json('2.4.0'):
            raise NotImplementedError("trusted is not supported on model version {}".format(self.model.info.agent_version))

        app_facade = self._facade()

        log.debug(
            'Getting config for %s', self.name)

        config = await app_facade.Get(application=self.name)
        if 'trust' in config.config:
            return config.config['trust']['value'] is True

        app_config = config.application_config
        return app_config['trust']['value'] is True

    async def set_trusted(self, trust):
        """Set the trusted configuration of the application.

        :param bool trust: Trust the application or not
        """
        if self.model.info.agent_version < client.Number.from_json('2.4.0'):
            raise NotImplementedError("trusted is not supported on model version {}".format(self.model.info.agent_version))

        # clamp trust to exactly the value juju expects, rather than allowing
        # anything in the config.
        app_facade = self._facade()

        config = {'trust': json.dumps(True if trust is True else False)}
        log.debug(
            'Setting config for %s: %s', self.name, config)

        # Unfortunately we have to do this in a lazy fashion, attempting to use
        # the method early will cause an error. Attempting to call this
        # dynamically causes issues with how the client code is wired up... we
        # end up with a missing _toPy attr.
        # Using a lambda to only throw it away when it's wrong seems a problem
        # as well.
        config_method = None
        if self._facade_version() < 13:
            config_method = app_facade.SetApplicationsConfig
        else:
            config_method = app_facade.SetConfigs
        return await config_method(args=[{
            "application": self.name,
            "config": config,
        }])

    async def get_constraints(self):
        """Return the machine constraints dict for this application.

        """
        app_facade = self._facade()

        log.debug(
            'Getting constraints for %s', self.name)

        result = (await app_facade.Get(application=self.name)).constraints
        return vars(result) if result else result

    async def get_actions(self, schema=False):
        """Get actions defined for this application.

        :param bool schema: Return the full action schema
        :return dict: The charms actions, empty dict if none are defined.
        """
        actions = {}
        entity = {"tag": self.tag}
        action_facade = client.ActionFacade.from_connection(self.connection)
        results = (await action_facade.ApplicationsCharmsActions(entities=[entity])).results
        for result in results:
            if result.application_tag == self.tag and result.actions:
                actions = result.actions
                break
        if not schema:
            actions = {k: v.description for k, v in actions.items()}
        return actions

    async def get_status(self):
        """Get the application status using info from the FullStatus
        as well, because it might be more up to date than our model

        :return: str status
        """

        client_facade = client.ClientFacade.from_connection(self.connection)

        full_status = await client_facade.FullStatus(patterns=None)
        _app = full_status.applications.get(self.name, None)
        if not _app:
            raise JujuError(f"application is not in FullStatus : {self.name}")

        self._status = derive_status([self.status, _app.status.status])
        return self._status

    def attach_resource(self, resource_name, file_name, file_obj):
        """Updates the resource for an application by uploading file from
        local disk to the Juju controller.

        :param str resource_name: Name of the resource to be updated.
        :param str file_name: Name of the local file to be uploaded.
        :param TextIOWrapper file_obj: Actual object to be read for data.
        """
        conn, headers, path_prefix = self.connection.https_connection()

        url = "{}/applications/{}/resources/{}".format(
            path_prefix, self.name, resource_name)

        data = file_obj.read()

        headers['Content-Type'] = 'application/octet-stream'
        headers['Content-Length'] = len(data)
        data_bytes = data if isinstance(data, bytes) else bytes(data, 'utf-8')
        headers['Content-Sha384'] = hashlib.sha384(data_bytes).hexdigest()

        file_name = str(file_name)
        if not file_name.startswith('./'):
            file_name = './' + file_name

        headers['Content-Disposition'] = "form-data; filename=\"{}\"".format(file_name)
        headers['Accept-Encoding'] = 'gzip'
        headers['Bakery-Protocol-Version'] = 3
        headers['Connection'] = 'close'

        conn.request('PUT', url, data, headers)
        response = conn.getresponse()
        result = response.read().decode()
        if not response.status == 200:
            raise JujuError(result)

    async def get_resources(self):
        """Return resources for this application.

        Returns a dict mapping resource name to
        :class:`~juju._definitions.CharmResource` instances.
        """
        facade = client.ResourcesFacade.from_connection(self.connection)
        response = await facade.ListResources(entities=[client.Entity(self.tag)])

        resources = dict()
        for result in response.results:
            for resource in result.charm_store_resources or []:
                resources[resource.name] = resource
            for resource in result.resources or []:
                if resource.charmresource:
                    resource = resource.charmresource
                    resources[resource.name] = resource
        return resources

    async def run(self, command, timeout=None):
        """Run command on all units for this application.

        :param str command: The command to run
        :param int timeout: Time to wait before command is considered failed

        """
        action = client.ActionFacade.from_connection(self.connection)

        log.debug(
            'Running `%s` on all units of %s', command, self.name)

        # TODO this should return a list of Actions
        return await action.Run(
            applications=[self.name],
            commands=command,
            machines=[],
            timeout=timeout,
            units=[],
        )

    @property
    def charm_name(self):
        """Get the charm name of this application

        :return str: The name of the charm
        """
        return URL.parse(self.charm_url).name

    @property
    def charm_url(self):
        """Get the charm url for this application

        :return str: The charm url
        """
        return self.safe_data['charm-url']

    async def get_annotations(self):
        """Get annotations on this application.

        :return dict: The annotations for this application
        """
        return await _get_annotations(self.tag, self.connection)

    async def set_annotations(self, annotations):
        """Set annotations on this application.

        :param annotations map[string]string: the annotations as key/value
            pairs.

        """
        return await _set_annotations(self.tag, annotations, self.connection)

    async def set_config(self, config):
        """Set configuration options for this application.

        :param config: Dict of configuration to set
        """
        app_facade = self._facade()

        log.debug(
            'Setting config for %s: %s', self.name, config)

        str_config = {}
        for k, v in config.items():
            if isinstance(v, str):
                str_config[k] = v
            elif isinstance(v, dict):
                # pairs with a value of None are ignored
                if v.get('value', False):
                    str_config[k] = str(v.get('value'))
            else:
                raise JujuApplicationConfigError(config, [k, v])

        return await app_facade.SetConfigs(args=[{
            "application": self.name,
            "config": str_config,
        }])

    async def reset_config(self, to_default):
        """
        Restore application config to default values.

        :param list to_default: A list of config options to be reset to their
        default value.
        """
        app_facade = self._facade()

        log.debug(
            'Restoring default config for %s: %s', self.name, to_default)

        return await app_facade.UnsetApplicationsConfig(args=[{
            "application": self.name,
            "options": to_default,
        }])

    async def set_constraints(self, constraints):
        """Set machine constraints for this application.

        :param dict constraints: Dict of machine constraints

        """
        app_facade = self._facade()

        log.debug(
            'Setting constraints for %s: %s', self.name, constraints)

        return await app_facade.SetConstraints(application=self.name, constraints=constraints)

    async def refresh(
            self, channel=None, force=False, force_series=False, force_units=False,
            path=None, resources=None, revision=None, switch=None):
        """Refresh the charm for this application.

        :param str channel: Channel to use when getting the charm from the
            charm store, e.g. 'development'
        :param bool force_series: Refresh even if series of deployed
            application is not supported by the new charm
        :param bool force_units: Refresh all units immediately, even if in
            error state
        :param str path: Refresh to a charm located at path
        :param dict resources: Dictionary of resource name/filepath pairs
        :param int revision: Explicit refresh revision
        :param str switch: Crossgrade charm url

        """
        if switch is not None and path is not None:
            raise ValueError("switch and path are mutually exclusive")

        if switch is not None and revision is not None:
            raise ValueError("switch and revision are mutually exclusive")

        app_facade = self._facade()
        charms_facade = client.CharmsFacade.from_connection(self.connection)

        # 1 - Figure out the destination origin and destination charm_url
        # 2 - Then take care of the resources
        # 3 - Finally execute the upgrade

        # Get the charm URL and charm origin of the given application is running at present.
        charm_url_origin_result = await app_facade.GetCharmURLOrigin(application=self.name)
        if charm_url_origin_result.error is not None:
            err = charm_url_origin_result.error
            raise JujuError(f'{err.code} : {err.message}')
        origin = charm_url_origin_result.charm_origin

        if path is not None or (switch is not None and is_local_charm(switch)):
            await self.local_refresh(origin, force, force_series,
                                     force_units, path or switch, resources)
            return

        # If switch is not None at this point, that means it's a switch to a store charm
        charm_url = switch or charm_url_origin_result.url
        parsed_url = URL.parse(charm_url)
        charm_name = parsed_url.name

        if parsed_url.schema is None:
            raise JujuError(f'A ch: or cs: schema is required for application refresh, given : {str(parsed_url)}')

        if revision is not None:
            origin.revision = revision

        # Make the source-specific changes to the origin/channel/url
        # (and also get the resources necessary to deploy the (destination) charm -- for later)
        origin.source = Source.CHARM_HUB.value
        if channel:
            ch = Channel.parse(channel).normalize()
            origin.risk = ch.risk
            origin.track = ch.track

        charmhub = self.model.charmhub
        charm_resources = await charmhub.list_resources(charm_name)

        # Resolve the given charm URLs with an optionally specified preferred channel.
        # Channel provided via CharmOrigin.
        resolved_charm_with_channel_results = await charms_facade.ResolveCharms(
            resolve=[client.ResolveCharmWithChannel(
                charm_origin=origin,
                switch_charm=True if switch else False,  # rpc expects boolean type
                reference=charm_url,
            )])
        resolved_charm = resolved_charm_with_channel_results.results[0]

        # Get the destination origin and destination charm_url from the resolved charm
        if resolved_charm.error is not None:
            err = resolved_charm.error
            raise JujuError(f'{err.code} : {err.message}')
        dest_origin = resolved_charm.charm_origin
        charm_url = resolved_charm.url

        # Add the charm with the destination url and origin
        charm_origin_result = await charms_facade.AddCharm(url=charm_url,
                                                           force=force,
                                                           charm_origin=dest_origin)
        if charm_origin_result.error is not None:
            err = charm_origin_result.error
            raise JujuError(f'{err.code} : {err.message}')

        # Now take care of the resources:

        # user supplied resources to be used in refresh,
        # will override the default values if there's any
        arg_resources = resources or {}

        # need to process the given resources, as they can be
        # paths or revisions
        _arg_res_filenames = {}
        _arg_res_revisions = {}
        for res, filename_or_rev in arg_resources.items():
            if isinstance(filename_or_rev, int):
                _arg_res_revisions[res] = filename_or_rev
            else:
                _arg_res_filenames[res] = filename_or_rev

        # Already prepped the charm_resources
        # Now get the existing resources from the ResourcesFacade
        request_data = [client.Entity(self.tag)]
        resources_facade = client.ResourcesFacade.from_connection(self.connection)
        response = await resources_facade.ListResources(entities=request_data)
        existing_resources = {
            resource.name: resource
            for resource in response.results[0].resources
        }

        # Compute the difference btw resources needed and the existing resources
        resources_to_update = []
        for resource in charm_resources:
            if utils.should_upgrade_resource(resource, existing_resources, arg_resources):
                resources_to_update.append(resource)

        # Update the resources
        if resources_to_update:
            request_data = []
            for resource in resources_to_update:
                res_name = resource.get('Name', resource.get('name'))
                request_data.append(client.CharmResource(
                    description=resource.get('Description', resource.get('description')),
                    name=res_name,
                    path=_arg_res_filenames.get(res_name,
                                                resource.get('Path',
                                                             resource.get('filename', ''))),
                    revision=_arg_res_revisions.get(res_name, -1),
                    type_=resource.get('Type', resource.get('type')),
                    origin='store',
                ))

            response = await resources_facade.AddPendingResources(
                application_tag=self.tag,
                charm_url=charm_url,
                resources=request_data,
                charm_origin=dest_origin,
            )
            pending_ids = response.pending_ids
            resource_ids = {
                resource.get('Name', resource.get('name')): id
                for resource, id in zip(resources_to_update, pending_ids)
            }
        else:
            resource_ids = None

        set_charm_args = {
            'application': self.entity_id,
            'charm_url': charm_url,
            'charm_origin': dest_origin,
            'config_settings': None,
            'config_settings_yaml': None,
            'force': force,
            'force_units': force_units,
            'resource_ids': resource_ids,
            'storage_constraints': None,
        }
        if self.connection.is_using_old_client:
            set_charm_args['force_series'] = force_series

        # Update the application
        await app_facade.SetCharm(**set_charm_args)

        await self.model.block_until(
            lambda: self.data['charm-url'] == charm_url
        )

    upgrade_charm = refresh

    async def local_refresh(
            self, charm_origin=None, force=False, force_series=False,
            force_units=False,
            path=None, resources=None):
        """Refresh the charm for this application with a local charm.

        :param dict charm_origin: The charm origin of the destination charm
            we're refreshing to
        :param bool force: Refresh even if validation checks fail
        :param bool force_series: Refresh even if series of deployed
            application is not supported by the new charm
        :param bool force_units: Refresh all units immediately, even if in
            error state
        :param str path: Refresh to a charm located at path
        :param dict resources: Dictionary of resource name/filepath pairs

        """
        app_facade = self._facade()

        if isinstance(path, str) and path.startswith("local:"):
            path = path[6:]
        path = Path(path)
        charm_dir = path.expanduser().resolve()
        model_config = await self.get_config()

        series = (
            await self.get_series() or
            self.model.info.get('default-series', '')
        )
        if not series:
            metadata = utils.get_local_charm_metadata(charm_dir)
            await get_charm_series(metadata, self.model)

        if not series:
            default_series = model_config.get("default-series")
            if default_series:
                series = default_series.value
        charm_url = await self.model.add_local_charm_dir(charm_dir, series)
        metadata = utils.get_local_charm_metadata(path)
        if resources is not None:
            resources = await self.model.add_local_resources(self.entity_id,
                                                             charm_url,
                                                             metadata,
                                                             resources=resources)

        # We know this charm is a local charm, but this charm origin could be
        # the charm origin of a charmhub charm. Ensure that we update/remove
        # the appropriate fields.
        charm_origin.source = "local"
        charm_origin.track = None
        charm_origin.risk = None
        charm_origin.branch = None
        charm_origin.hash_ = None
        charm_origin.id_ = None
        charm_origin.revision = URL.parse(charm_url).revision

        set_charm_args = {
            'application': self.entity_id,
            'charm_origin': charm_origin,
            'charm_url': charm_url,
            'config_settings': None,
            'config_settings_yaml': None,
            'force': force,
            'force_units': force_units,
            'resource_ids': resources,
            'storage_constraints': None,
        }

        if self.connection.is_using_old_client:
            set_charm_args['force_series'] = force_series

        # Update application
        await app_facade.SetCharm(**set_charm_args)

        await self.model.block_until(
            lambda: self.data['charm-url'] == charm_url
        )

    async def get_metrics(self):
        """Get metrics for this application's units.

        :return: Dictionary of unit_name:metrics

        """
        return await self.model.get_metrics(self.tag)


class ExposedEndpoint:
    """ExposedEndpoint stores the list of CIDRs and space names which should be
    allowed access to the port ranges that the application has opened for a
    particular endpoint. Both lists are optional; if empty, the opened port
    ranges will be reachable from any source IP address."""

    def __init__(self, to_spaces=None, to_cidrs=None):
        if to_spaces is not None and not isinstance(to_spaces, list):
            raise ValueError("to_spaces must be a list of space names or None")
        if to_cidrs is not None and not isinstance(to_cidrs, list):
            raise ValueError("to_cidrs must be a list of CIDRs or None")

        self.to_cidrs = to_cidrs
        self.to_spaces = to_spaces

    def includes_spaces(self):
        return self.to_spaces is not None and len(self.to_spaces) > 0

    def includes_non_wildcard_cidrs(self):
        to_cidrs = (self.to_cidrs or [])
        non_wildcard_cidrs = filter(lambda x: x == "0.0.0.0/0" or x == "::/0",
                                    to_cidrs)
        return len(list(non_wildcard_cidrs)) > 0

    @classmethod
    def from_dict(cls, data):
        d = (data or {})
        if not isinstance(d, dict):
            raise ValueError("expected a dictionary with fields: expose-to-spaces and expose-to-cidrs")

        to_spaces = None
        if "expose-to-spaces" in d and isinstance(d["expose-to-spaces"], list):
            to_spaces = d["expose-to-spaces"]
        to_cidrs = None
        if "expose-to-cidrs" in d and isinstance(d["expose-to-cidrs"], list):
            to_cidrs = d["expose-to-cidrs"]

        return cls(to_spaces=to_spaces, to_cidrs=to_cidrs)

    def to_dict(self):
        d = {}
        if self.to_cidrs is not None:
            d["expose-to-cidrs"] = self.to_cidrs
        if self.to_spaces is not None:
            d["expose-to-spaces"] = self.to_spaces
        return d

    def __str__(self):
        descr = ""
        if self.to_spaces is not None and len(self.to_spaces) > 0:
            if len(self.to_spaces) == 1:
                descr = "from space {}".format(self.to_spaces[0])
            elif len(self.to_spaces) > 1:
                descr = "from spaces {}".format(",".join(self.to_spaces))

            if self.to_cidrs is not None and len(self.to_cidrs) > 0:
                descr = descr + " and "

        if self.to_cidrs is not None:
            if len(self.to_cidrs) == 1:
                descr = descr + "from CIDR {}".format(self.to_cidrs[0])
            elif len(self.to_cidrs) > 1:
                descr = descr + "from CIDRs {}".format(",".join(self.to_cidrs))

        return descr
