import asyncio
import logging

from . import model
from .client import client

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

    def add_relation(self, local_relation, remote_relation):
        """Add a relation to another service.

        :param str local_relation: Name of relation on this service
        :param str remote_relation: Name of relation on the other service in
            the form '<service>[:<relation_name>]'

        """
        pass

    async def add_unit(self, count=1, to=None):
        """Add one or more units to this service.

        :param int count: Number of units to add
        :param str to: Placement directive, e.g.::
            '23' - machine 23
            'lxc:7' - new lxc container on machine 7
            '24/lxc/3' - lxc container 3 or machine 24

            If None, a new machine is provisioned.

        """
        app_facade = client.ApplicationFacade()
        app_facade.connect(self.connection)

        log.debug(
            'Adding %s unit%s to %s',
            count, '' if count == 1 else 's', self.name)

        result = await app_facade.AddUnits(
            application=self.name,
            placement=to,
            num_units=count,
        )

        return await asyncio.gather(*[
            asyncio.ensure_future(self.model._wait_for_new('unit', unit_id))
            for unit_id in result.units
        ])

    add_units = add_unit

    def allocate(self, budget, value):
        """Allocate budget to this service.

        :param str budget: Name of budget
        :param int value: Budget limit

        """
        pass

    def attach(self, resource_name, file_path):
        """Upload a file as a resource for this service.

        :param str resource: Name of the resource
        :param str file_path: Path to the file to upload

        """
        pass

    def collect_metrics(self):
        """Collect metrics on this service.

        """
        pass

    def destroy_relation(self, local_relation, remote_relation):
        """Remove a relation to another service.

        :param str local_relation: Name of relation on this service
        :param str remote_relation: Name of relation on the other service in
            the form '<service>[:<relation_name>]'

        """
        pass
    remove_relation = destroy_relation

    async def destroy(self):
        """Remove this service from the model.

        """
        app_facade = client.ApplicationFacade()
        app_facade.connect(self.connection)

        log.debug(
            'Destroying %s', self.name)

        return await app_facade.Destroy(self.name)
    remove = destroy

    async def expose(self):
        """Make this service publicly available over the network.

        """
        app_facade = client.ApplicationFacade()
        app_facade.connect(self.connection)

        log.debug(
            'Exposing %s', self.name)

        return await app_facade.Expose(self.name)

    def get_config(self):
        """Return the configuration settings for this service.

        """
        pass

    def get_constraints(self):
        """Return the machine constraints for this service.

        """
        pass

    def get_actions(self, schema=False):
        """Get actions defined for this service.

        :param bool schema: Return the full action schema

        """
        pass

    def get_resources(self, details=False):
        """Return resources for this service.

        :param bool details: Include detailed info about resources used by each
            unit

        """
        pass

    def run(self, command, timeout=None):
        """Run command on all units for this service.

        :param str command: The command to run
        :param int timeout: Time to wait before command is considered failed

        """
        pass

    def set_config(self, to_default=False, **config):
        """Set configuration options for this service.

        :param bool to_default: Set service options to default values
        :param \*\*config: Config key/values

        """
        pass

    def set_constraints(self, constraints):
        """Set machine constraints for this service.

        :param :class:`juju.Constraints` constraints: Machine constraints

        """
        pass

    def set_meter_status(self, status, info=None):
        """Set the meter status on this status.

        :param str status: Meter status, e.g. 'RED', 'AMBER'
        :param str info: Extra info message

        """
        pass

    def set_plan(self, plan_name):
        """Set the plan for this service, effective immediately.

        :param str plan_name: Name of plan

        """
        pass

    def unexpose(self):
        """Remove public availability over the network for this service.

        """
        pass

    def update_allocation(self, allocation):
        """Update existing allocation for this service.

        :param int allocation: The allocation to set

        """
        pass

    def upgrade_charm(
            self, channel=None, force_series=False, force_units=False,
            path=None, resources=None, revision=-1, switch=None):
        """Upgrade the charm for this service.

        :param str channel: Channel to use when getting the charm from the
            charm store, e.g. 'development'
        :param bool force_series: Upgrade even if series of deployed service
            is not supported by the new charm
        :param bool force_units: Upgrade all units immediately, even if in
            error state
        :param str path: Uprade to a charm located at path
        :param dict resources: Dictionary of resource name/filepath pairs
        :param int revision: Explicit upgrade revision
        :param str switch: Crossgrade charm url

        """
        pass
