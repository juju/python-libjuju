""" derive_status is used to determine the application status from a set of unit
status values.

:param statues: list of known unit workload statues

"""


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
