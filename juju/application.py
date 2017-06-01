import asyncio
import logging

from . import model
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
        return 'application-%s' % self.name

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

        return await app_facade.DestroyRelation([
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

        return await app_facade.Destroy(self.name)
    remove = destroy

    async def expose(self):
        """Make this application publicly available over the network.

        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Exposing %s', self.name)

        return await app_facade.Expose(self.name)

    async def get_config(self):
        """Return the configuration settings dict for this application.

        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Getting config for %s', self.name)

        return (await app_facade.Get(self.name)).config

    async def get_constraints(self):
        """Return the machine constraints dict for this application.

        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Getting constraints for %s', self.name)

        result = (await app_facade.Get(self.name)).constraints
        return vars(result) if result else result

    def get_actions(self, schema=False):
        """Get actions defined for this application.

        :param bool schema: Return the full action schema

        """
        raise NotImplementedError()

    def get_resources(self, details=False):
        """Return resources for this application.

        :param bool details: Include detailed info about resources used by each
            unit

        """
        raise NotImplementedError()

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
            [self.name],
            command,
            [],
            timeout,
            [],
        )

    async def set_annotations(self, annotations):
        """Set annotations on this application.

        :param annotations map[string]string: the annotations as key/value
            pairs.

        """
        log.debug('Updating annotations on application %s', self.name)

        self.ann_facade = client.AnnotationsFacade.from_connection(
            self.connection)

        ann = client.EntityAnnotations(
            entity=self.tag,
            annotations=annotations,
        )
        return await self.ann_facade.Set([ann])

    async def set_config(self, config, to_default=False):
        """Set configuration options for this application.

        :param config: Dict of configuration to set
        :param bool to_default: Set application options to default values

        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Setting config for %s: %s', self.name, config)

        return await app_facade.Set(self.name, config)

    async def set_constraints(self, constraints):
        """Set machine constraints for this application.

        :param dict constraints: Dict of machine constraints

        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug(
            'Setting constraints for %s: %s', self.name, constraints)

        return await app_facade.SetConstraints(self.name, constraints)

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

        return await app_facade.Unexpose(self.name)

    def update_allocation(self, allocation):
        """Update existing allocation for this application.

        :param int allocation: The allocation to set

        """
        raise NotImplementedError()

    async def upgrade_charm(
            self, channel=None, force_series=False, force_units=False,
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
        app_facade = client.ApplicationFacade.from_connection(self.connection)

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
                charmstore = self.model.charmstore
                entity = await charmstore.entity(charm_url, channel=channel)
                charm_url = entity['Id']

        if charm_url == self.data['charm-url']:
            raise JujuError('already running charm "%s"' % charm_url)

        await client_facade.AddCharm(
            url=charm_url,
            channel=channel
        )

        await app_facade.SetCharm(
            application=self.entity_id,
            channel=channel,
            charm_url=charm_url,
            config_settings=None,
            config_settings_yaml=None,
            force_series=force_series,
            force_units=force_units,
            resource_ids=None,
            storage_constraints=None
        )

        await self.model.block_until(
            lambda: self.data['charm-url'] == charm_url
        )

    async def get_metrics(self):
        """Get metrics for this application's units.

        :return: Dictionary of unit_name:metrics

        """
        return await self.model.get_metrics(self.tag)
