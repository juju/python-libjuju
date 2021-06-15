# Copyright 2016 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import asyncio
import json
import logging
import os

from . import model, tag
from .status import derive_status
from .annotationhelper import _get_annotations, _set_annotations
from .client import client
from .errors import JujuError
from .bundle import get_charm_series
from .placement import parse as parse_placement
from .charm import get_local_charm_metadata

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
            unit_status = []
            for unit in self.units:
                unit_status.append(unit.workload_status)
            return derive_status(unit_status)
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
        """Add a relation to another application.

        :param str local_relation: Name of relation on this application
        :param str remote_relation: Name of relation on the other
            application in the form '<application>[:<relation_name>]'

        """
        if ':' not in local_relation:
            local_relation = '{}:{}'.format(self.name, local_relation)

        return await self.model.add_relation(local_relation, remote_relation)

    async def add_unit(self, count=1, to=None):
        """Add one or more units to this application.

        :param int count: Number of units to add
        :param str to: Placement directive, e.g.::
            '23' - machine 23
            'lxc:7' - new lxc container on machine 7
            '24/lxc/3' - lxc container 3 or machine 24

            If None, a new machine is provisioned.

        """
        app_facade = self._facade()

        log.debug(
            'Adding %s unit%s to %s',
            count, '' if count == 1 else 's', self.name)

        result = await app_facade.AddUnits(
            application=self.name,
            placement=parse_placement(to) if to else None,
            num_units=count,
        )

        return await asyncio.gather(*[
            asyncio.ensure_future(self.model._wait_for_new('unit', unit_id))
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

    def allocate(self, budget, value):
        """Allocate budget to this application.

        :param str budget: Name of budget
        :param int value: Budget limit

        """
        raise NotImplementedError()

    def attach(self, resource_name, file_path):
        """Upload a file as a resource for this application.

        :param str resource: Name of the resource
        :param str file_path: Path to the file to upload

        """
        raise NotImplementedError()

    def collect_metrics(self):
        """Collect metrics on this application.

        """
        raise NotImplementedError()

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

    async def destroy(self):
        """Remove this application from the model.

        """
        app_facade = self._facade()

        log.debug(
            'Destroying %s', self.name)

        return await app_facade.Destroy(application=self.name)
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
        entity = [{"tag": self.tag}]
        action_facade = client.ActionFacade.from_connection(self.connection)
        results = (
            await action_facade.ApplicationsCharmsActions(entities=entity)).results
        for result in results:
            if result.application_tag == self.tag and result.actions:
                actions = result.actions
                break
        if not schema:
            actions = {k: v.description for k, v in actions.items()}
        return actions

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

        return await app_facade.Set(application=self.name, options=config)

    async def reset_config(self, to_default):
        """
        Restore application config to default values.

        :param list to_default: A list of config options to be reset to their
        default value.
        """
        app_facade = self._facade()

        log.debug(
            'Restoring default config for %s: %s', self.name, to_default)

        return await app_facade.Unset(application=self.name, options=to_default)

    async def set_constraints(self, constraints):
        """Set machine constraints for this application.

        :param dict constraints: Dict of machine constraints

        """
        app_facade = self._facade()

        log.debug(
            'Setting constraints for %s: %s', self.name, constraints)

        return await app_facade.SetConstraints(application=self.name, constraints=constraints)

    def set_meter_status(self, status, info=None):
        """Set the meter status on this status.

        :param str status: Meter status, e.g. 'RED', 'AMBER'
        :param str info: Extra info message

        """
        raise NotImplementedError()

    def set_plan(self, plan_name):
        """Set the plan for this application, effective immediately.

        :param str plan_name: Name of plan

        """
        raise NotImplementedError()

    def update_allocation(self, allocation):
        """Update existing allocation for this application.

        :param int allocation: The allocation to set

        """
        raise NotImplementedError()

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
        if path is not None:
            await self.local_refresh(channel, force, force_series, force_units,
                                     path, resources)
            return
        if resources is not None:
            raise NotImplementedError("resources option is not implemented")

        if switch is not None and revision is not None:
            raise ValueError("switch and revision are mutually exclusive")

        client_facade = client.ClientFacade.from_connection(self.connection)
        resources_facade = client.ResourcesFacade.from_connection(
            self.connection)
        app_facade = self._facade()

        charmstore = self.model.charmstore
        charmstore_entity = None

        if switch is not None:
            charm_url = switch
            if not charm_url.startswith('cs:'):
                charm_url = 'cs:' + charm_url
        else:
            charm_url = self.data['charm-url']
            charm_url = charm_url.rpartition('-')[0]
            if revision is not None:
                charm_url = "%s-%d" % (charm_url, revision)
            else:
                charmstore_entity = await charmstore.entity(charm_url,
                                                            channel=channel)
                charm_url = charmstore_entity['Id']

        if charm_url == self.data['charm-url']:
            raise JujuError('already running charm "%s"' % charm_url)

        # Update charm
        await client_facade.AddCharm(
            url=charm_url,
            force=force,
            channel=channel
        )

        # Update resources
        if not charmstore_entity:
            charmstore_entity = await charmstore.entity(charm_url,
                                                        channel=channel)
        store_resources = charmstore_entity['Meta']['resources']

        request_data = [client.Entity(self.tag)]
        response = await resources_facade.ListResources(entities=request_data)
        existing_resources = {
            resource.name: resource
            for resource in response.results[0].resources
        }

        resources_to_update = [
            resource for resource in store_resources
            if resource['Name'] not in existing_resources or
            existing_resources[resource['Name']].origin != 'upload'
        ]

        if resources_to_update:
            request_data = [
                client.CharmResource(
                    description=resource.get('Description'),
                    fingerprint=resource['Fingerprint'],
                    name=resource['Name'],
                    path=resource['Path'],
                    revision=resource['Revision'],
                    size=resource['Size'],
                    type_=resource['Type'],
                    origin='store',
                ) for resource in resources_to_update
            ]
            response = await resources_facade.AddPendingResources(
                application_tag=self.tag,
                charm_url=charm_url,
                resources=request_data
            )
            pending_ids = response.pending_ids
            resource_ids = {
                resource['Name']: id
                for resource, id in zip(resources_to_update, pending_ids)
            }
        else:
            resource_ids = None

        # Update application
        await app_facade.SetCharm(
            application=self.entity_id,
            channel=channel,
            charm_url=charm_url,
            config_settings=None,
            config_settings_yaml=None,
            force=force,
            force_series=force_series,
            force_units=force_units,
            resource_ids=resource_ids,
            storage_constraints=None,
        )

        await self.model.block_until(
            lambda: self.data['charm-url'] == charm_url
        )

    upgrade_charm = refresh

    async def local_refresh(
            self, channel=None, force=False, force_series=False, force_units=False,
            path=None, resources=None):
        """Refresh the charm for this application with a local charm.

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
        app_facade = self._facade()

        charm_dir = os.path.abspath(
            os.path.expanduser(path))
        model_config = await self.get_config()

        series = get_charm_series(charm_dir)
        if not series:
            model_config = await self.get_config()
            default_series = model_config.get("default-series")
            if default_series:
                series = default_series.value
        charm_url = await self.model.add_local_charm_dir(charm_dir, series)
        metadata = get_local_charm_metadata(path)
        if resources is not None:
            resources = await self.model.add_local_resources(self.entity_id,
                                                             charm_url,
                                                             metadata,
                                                             resources=resources)

        # Update application
        await app_facade.SetCharm(
            application=self.entity_id,
            channel=channel,
            charm_url=charm_url,
            config_settings=None,
            config_settings_yaml=None,
            force=force,
            force_series=force_series,
            force_units=force_units,
            resource_ids=resources,
            storage_constraints=None,
        )

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
