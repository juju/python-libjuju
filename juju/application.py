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

from . import model, tag
from .annotationhelper import _get_annotations, _set_annotations
from .client import client
from .errors import JujuError
from .placement import parse as parse_placement

log = logging.getLogger(__name__)


class Application(model.ModelEntity):
    @property
    def _unit_match_pattern(self):
        return r'^{}.*$'.format(self.entity_id)

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
        """Get the application status, as set by the charm's leader.

        """
        return self.safe_data['status']['current']

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
        app_facade = client.ApplicationFacade.from_connection(self.connection)

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
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        if (scale, scale_change) == (None, None):
            raise ValueError('Must provide either scale or scale_change')

        log.debug(
            'Scaling application %s %s %s',
            self.name, 'to' if scale else 'by', scale or scale_change)

        await app_facade.ScaleApplications(applications=[
            client.ScaleApplicationParam(application_tag=self.tag,
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

        app_facade = client.ApplicationFacade.from_connection(self.connection)

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
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Destroying %s', self.name)

        return await app_facade.Destroy(application=self.name)
    remove = destroy

    async def expose(self):
        """Make this application publicly available over the network.

        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Exposing %s', self.name)

        return await app_facade.Expose(application=self.name)

    async def get_config(self):
        """Return the configuration settings dict for this application.

        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Getting config for %s', self.name)

        return (await app_facade.Get(application=self.name)).config

    async def get_trusted(self):
        """Return the trusted configuration setting for this application.

        """
        if self.model.info.agent_version < client.Number.from_json('2.4.0'):
            raise NotImplementedError("trusted is not supported on model version {}".format(self.model.info.agent_version))

        app_facade = client.ApplicationFacade.from_connection(self.connection)

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
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        config = {'trust': json.dumps(True if trust is True else False)}
        log.debug(
            'Setting config for %s: %s', self.name, config)

        return await app_facade.SetApplicationsConfig(args=[{
            "application": self.name,
            "config": config,
        }])

    async def get_constraints(self):
        """Return the machine constraints dict for this application.

        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

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
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Setting config for %s: %s', self.name, config)

        return await app_facade.Set(application=self.name, options=config)

    async def reset_config(self, to_default):
        """
        Restore application config to default values.

        :param list to_default: A list of config options to be reset to their
        default value.
        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Restoring default config for %s: %s', self.name, to_default)

        return await app_facade.Unset(application=self.name, options=to_default)

    async def set_constraints(self, constraints):
        """Set machine constraints for this application.

        :param dict constraints: Dict of machine constraints

        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

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

    async def unexpose(self):
        """Remove public availability over the network for this application.

        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Unexposing %s', self.name)

        return await app_facade.Unexpose(application=self.name)

    def update_allocation(self, allocation):
        """Update existing allocation for this application.

        :param int allocation: The allocation to set

        """
        raise NotImplementedError()

    async def upgrade_charm(
            self, channel=None, force=False, force_series=False, force_units=False,
            path=None, resources=None, revision=None, switch=None):
        """Upgrade the charm for this application.

        :param str channel: Channel to use when getting the charm from the
            charm store, e.g. 'development'
        :param bool force_series: Upgrade even if series of deployed
            application is not supported by the new charm
        :param bool force_units: Upgrade all units immediately, even if in
            error state
        :param str path: Uprade to a charm located at path
        :param dict resources: Dictionary of resource name/filepath pairs
        :param int revision: Explicit upgrade revision
        :param str switch: Crossgrade charm url

        """
        # TODO: Support local upgrades
        if path is not None:
            raise NotImplementedError("path option is not implemented")
        if resources is not None:
            raise NotImplementedError("resources option is not implemented")

        if switch is not None and revision is not None:
            raise ValueError("switch and revision are mutually exclusive")

        client_facade = client.ClientFacade.from_connection(self.connection)
        resources_facade = client.ResourcesFacade.from_connection(
            self.connection)
        app_facade = client.ApplicationFacade.from_connection(self.connection)

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

    async def get_metrics(self):
        """Get metrics for this application's units.

        :return: Dictionary of unit_name:metrics

        """
        return await self.model.get_metrics(self.tag)
