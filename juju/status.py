# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import logging
from typing import Literal, Union

from .client import client

log = logging.getLogger(__name__)

""" derive_status is used to determine the application status from a set of unit
status values.

:param statues: list of known unit workload statues

"""

# Status values common to machine and unit agents.
CommonStatusT = Literal['error', 'started']

# Error means the entity requires human intervention
# in order to operate correctly.
ERROR: CommonStatusT = 'error'

# Started is set when:
# The entity is actively participating in the model.
# For unit agents, this is a state we preserve for backwards
# compatibility with scripts during the life of Juju 1.x.
# In Juju 2.x, the agent-state will remain “active” and scripts
# will watch the unit-state instead for signals of application readiness.
STARTED: CommonStatusT = 'started'


# Status values specific to machine agents.
MachineAgentStatusT = Union[Literal['pending', 'stopped', 'down'], CommonStatusT]

# Pending is set when:
# The machine is not yet participating in the model.
PENDING: MachineAgentStatusT = 'pending'

# Stopped is set when:
# The machine's agent will perform no further action, other than
# to set the unit to Dead at a suitable moment.
STOPPED: MachineAgentStatusT = 'stopped'

# Down is set when:
# The machine ought to be signalling activity, but it cannot be
# detected.
DOWN: MachineAgentStatusT = 'down'


# Status values specific to unit agents.
UnitAgentStatusT = Union[
    Literal['allocating', 'rebooting', 'executing', 'idle', 'failed', 'lost'],
    CommonStatusT,
]

# Allocating is set when:
# The machine on which a unit is to be hosted is still being
# spun up in the cloud.
ALLOCATING: UnitAgentStatusT = 'allocating'

# Rebooting is set when:
# The machine on which this agent is running is being rebooted.
# The juju-agent should move from rebooting to idle when the reboot is complete.
REBOOTING: UnitAgentStatusT = 'rebooting'

# Executing is set when:
# The agent is running a hook or action. The human-readable message should reflect
# which hook or action is being run.
EXECUTING: UnitAgentStatusT = 'executing'

# Idle is set when:
# Once the agent is installed and running it will notify the Juju server and its state
# becomes 'idle'. It will stay 'idle' until some action (e.g. it needs to run a hook) or
# error (e.g it loses contact with the Juju server) moves it to a different state.
IDLE: UnitAgentStatusT = 'idle'

# Failed is set when:
# The unit agent has failed in some way,eg the agent ought to be signalling
# activity, but it cannot be detected. It might also be that the unit agent
# detected an unrecoverable condition and managed to tell the Juju server about it.
FAILED: UnitAgentStatusT = 'failed'

# Lost is set when:
# The juju agent has not communicated with the juju server for an unexpectedly long time;
# the unit agent ought to be signalling activity, but none has been detected.
LOST: UnitAgentStatusT = 'lost'

# Status values specific to applications and units, reflecting the
# state of the software itself.
AppOrUnitStatusT = Literal[
    'unset', 'maintenance', 'terminated', 'unknown', 'waiting', 'blocked', 'active'
]
# Unset is only for applications, and is a placeholder status.
# The core/cache package deals with aggregating the unit status
# to the application level.
UNSET: AppOrUnitStatusT = 'unset'

# Maintenance is set when:
# The unit is not yet providing services, but is actively doing stuff
# in preparation for providing those services.
# This is a 'spinning' state, not an error state.
# It reflects activity on the unit itself, not on peers or related units.
MAINTENANCE: AppOrUnitStatusT = 'maintenance'

# Terminated is set when:
# This unit used to exist, we have a record of it (perhaps because of storage
# allocated for it that was flagged to survive it). Nonetheless, it is now gone.
TERMINATED: AppOrUnitStatusT = 'terminated'

# Unknown is set when:
# A unit-agent has finished calling install, config-changed, and start,
# but the charm has not called : AppOrUnitStatusT-set yet.
UNKNOWN: AppOrUnitStatusT = 'unknown'

# Waiting is set when:
# The unit is unable to progress to an active state because an application to
# which it is related is not running.
WAITING: AppOrUnitStatusT = 'waiting'

# Blocked is set when:
# The unit needs manual intervention to get back to the Running state.
BLOCKED: AppOrUnitStatusT = 'blocked'

# Active is set when:
# The unit believes it is correctly offering all the services it has
# been asked to offer.
ACTIVE: AppOrUnitStatusT = 'active'

# Status values specific to storage.
StorageStatusT = Literal['attaching', 'attached', 'detaching', 'detached']

# Attaching indicates that the storage is being attached
# to a machine.
ATTACHING: StorageStatusT = 'attaching'

# Attached indicates that the storage is attached to a
# machine.
ATTACHED: StorageStatusT = 'attached'

# Detaching indicates that the storage is being detached
# from a machine.
DETACHING: StorageStatusT = 'detaching'

# Detached indicates that the storage is not attached to
# any machine.
DETACHED: StorageStatusT = 'detached'

# Status values specific to models.
ModelStatusT = Literal['available', 'busy']

# Available indicates that the model is available for use.
AVAILABLE: ModelStatusT = 'available'

# Busy indicates that the model is not available for use because it is
# running a process that must take the model offline, such as a migration,
# upgrade, or backup.  This is a spinning state, it is not an error state,
# and it should be expected that the model will eventually go back to
# available.
BUSY: ModelStatusT = 'busy'

# Status values specific to relations.
RelationStatusT = Literal['joining', 'joined', 'broken', 'suspending']

# Joining is used to signify that a relation should become joined soon.
JOINING: RelationStatusT = 'joining'

# Joined is the normal : RelationStatusT for a healthy, alive relation.
JOINED: RelationStatusT = 'joined'

# Broken is the : RelationStatusT for when a relation life goes to Dead.
BROKEN: RelationStatusT = 'broken'

# Suspending is used to signify that a relation will be temporarily broken
# pending action to resume it.
SUSPENDING: RelationStatusT = 'suspending'

# Suspended is used to signify that a relation is temporarily broken pending
# action to resume it.
SUSPENDED: RelationStatusT = 'suspended'

# Status values that are common to several entities.
CommonEntityStatusT = Literal['destroying']

# Destroying indicates that the entity is being destroyed.
# This is valid for volumes, filesystems, and models.
DESTROYING: CommonEntityStatusT = 'destroying'

# InstanceStatus
InstanceStatusT = Literal['', 'allocating', 'running', 'provisioning error']
EMPTY: InstanceStatusT = ''
PROVISIONING: InstanceStatusT = 'allocating'
RUNNING: InstanceStatusT = 'running'
PROVISIONING_ERROR: InstanceStatusT = 'provisioning error'

# ModificationStatus
ModificationStatusT = Literal['applied']
APPLIED: ModificationStatusT = 'applied'

# Messages
MESSAGE_WAIT_FOR_MACHINE = 'waiting for machine'
MESSAGE_WAIT_FOR_CONTAINER = 'waiting for container'
MESSAGE_INSTALLING_AGENT = 'installing agent'
MESSAGE_INITIALIZING_AGENT = 'agent initialising'
MESSAGE_INSTALLING_CHARM = 'installing charm software'


def derive_status(statues):
    current = 'unknown'
    for status in statues:
        if status in serverities and serverities[status] > serverities[current]:
            current = status
    return current


""" serverities holds status values with a severity measure.
Status values with higher severity are used in preference to others.
"""
serverities = {
    'error': 100,
    'blocked': 90,
    'waiting': 80,
    'maintenance': 70,
    'active': 60,
    'terminated': 50,
    'unknown': 40
}


async def formatted_status(model, target=None, raw=False, filters=None):
    """Returns a string that mimics the content of the information
    returned in the juju status command. If the raw parameter is
    enabled, the function retursn a FullStatus object.
    :param Model model: model object to be used
    :param Fileobject target: if set expects a file object such as
        sys.stdout or a file descriptor. The obtained status will
        be sent to the file using the write function. If set to
        `None`, this function returns a string with the formatted
        status.
    :param bool raw: if `true` this functions returns the raw
        `FullStatus` object returned by Juju. This is similar to
        invoking `get_status`.
    :param str fileters: Optional list of applications, units, or machines
        to include, which can use wildcards ('*').
    """
    client_facade = client.ClientFacade.from_connection(model.connection())
    result_status = await client_facade.FullStatus(patterns=filters)

    if raw:
        result_str = str(result_status)
    else:
        result_str = _print_status_model(result_status)
        result_str += '\n'
        result_str += _print_status_apps(result_status)
        result_str += '\n'
        result_str += _print_status_units(result_status)
        result_str += '\n'
        result_str += _print_status_machines(result_status)
        result_str += '\n'
    if target is None:
        return result_str

    try:
        target.write(result_str)
    except Exception as e:
        logging.error(e)

    return None


def _print_status_model(result_status):
    """Private function to print the status of a model"""
    m = result_status.model
    # print model
    result_str = '{:<25} {:<25} {:<15} {:<15} {:<30} {:<30}\n'.format(
        'Model', 'Cloud/Region', 'Version', 'SLA', 'Timestamp', 'Notes')
    sla = m.unknown_fields['sla']
    cloud = m.cloud_tag.split('-')[1]
    timestamp = result_status.controller_timestamp
    if m.available_version is not None and m.available_version != '':
        available_version = 'upgrade available: {}'.format(m.available_version)
    else:
        available_version = ''
    result_str += '{:<25} {:<25} {:<15} {:<15} {:<30} {:<30}'.format(
        m.name, cloud + '/' + m.region, m.version, sla,
        timestamp, available_version)
    result_str += '\n'
    return result_str


def _print_status_apps(result_status):
    """Auxiliar function to print the apps received
    in a status result"""
    apps = result_status.applications
    if apps is None or len(apps) == 0:
        return ''

    limits = '{:<25} {:<10} {:<10} {:<5} {:<20} {:<8}'
    # print header
    result_str = limits.format(
        'App', 'Version', 'Status', 'Scale', 'Charm', 'Channel')

    for name, app in apps.items():
        # extract charm name from the path
        # like in ch:amd64/trusty/mediawiki-28
        charm_name = app.charm.split('/')[-1]
        charm_name = charm_name.split('-')[0]
        work_ver = 'NA' if app.workload_version is None else app.workload_version
        charm_channel = 'NA' if app.charm_channel is None else app.charm_channel
        app_units = 'NA' if app.units is None else len(app.units)
        app_status = 'NA' if app.status.status is None else app.status.status
        result_str += '\n'
        result_str += limits.format(
            name, work_ver, app_status, app_units, charm_name,
            charm_channel)
    result_str += '\n'
    return result_str


def _print_status_units(result_status):
    """Auxiliar function to print the units received
    in a status result"""

    apps = result_status.applications
    if apps is None or len(apps) == 0:
        return

    limits = '{:<15} {:<15} {:<20} {:<10} {:<15} {:<10} {:<30}'
    summary = ''
    for app_name, app in apps.items():
        units = app.units
        if units is None or len(units) == 0:
            next

        for name, unit in units.items():
            addr = unit.public_address
            if addr is None:
                addr = ''

            if unit.opened_ports is None:
                opened_ports = ''
            else:
                opened_ports = ','.join(unit.opened_ports)

            info = unit.workload_status.info
            if info is None:
                info = ''

            step = limits.format(
                name, unit.workload_status.status,
                unit.agent_status.status, unit.machine,
                addr, opened_ports, info)
            if summary == '':
                summary = step
            else:
                summary = summary + '\n' + step

    if len(summary) == 0:
        return ''
    result_str = limits.format(
        'Unit', 'Workload', 'Agent', 'Machine',
        'Public address', 'Ports', 'Message')
    result_str += '\n'
    result_str += summary
    result_str += '\n'
    return result_str


def _print_status_machines(result_status):
    machines = result_status.machines
    if machines is None or len(machines) == 0:
        return

    limits = '{:<15} {:<15} {:<15} {:<20} {:<15} {:<30}'
    summary = ''
    for name, machine in machines.items():
        dns = machine.dns_name
        if dns is None:
            dns = ''
        step = limits.format(
            name,
            machine.agent_status.status,
            dns,
            machine.instance_id,
            machine.series,
            machine.agent_status.info
        )
        if summary == '':
            summary = step
        else:
            summary = summary + '\n' + step

    if summary == '':
        return
    result_str = limits.format('Machine', 'State', 'DNS', 'Inst id', 'Series', 'Message')
    result_str += '\n'
    result_str += summary
    result_str += '\n'
    return result_str
