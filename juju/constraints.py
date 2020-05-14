#
# Module that parses constraints
#
# The current version of juju core expects the client to take
# constraints given in the form "mem=10G foo=bar" and parse them into
# json that looks like {"mem": 10240, "foo": "bar"}. This module helps us
# accomplish that task.
#
# We do not attempt to duplicate the checking done in
# client/_client.py:Value here. That class will verify that the
# constraints keys are valid, and that we can successfully dump the
# constraints dict to json.
#
# Once https://bugs.launchpad.net/juju/+bug/1645402 is addressed, this
# module should be deprecated.
#

import re

# Matches on a string specifying memory size
MEM = re.compile('^[1-9][0-9]*[MGTP]$')

# Multiplication factors to get Megabytes
# https://github.com/juju/juju/blob/master/constraints/constraints.go#L666
FACTORS = {
    "M": 1024 ** 0,
    "G": 1024 ** 1,
    "T": 1024 ** 2,
    "P": 1024 ** 3,
    "E": 1024 ** 4,
    "Z": 1024 ** 5,
    "Y": 1024 ** 6
}

LIST_KEYS = {'tags', 'spaces'}

SNAKE1 = re.compile(r'(.)([A-Z][a-z]+)')
SNAKE2 = re.compile('([a-z0-9])([A-Z])')


def parse(constraints):
    """
    Constraints must be expressed as a string containing only spaces
    and key value pairs joined by an '='.

    """
    if not constraints:
        return None

    if type(constraints) is dict:
        # Fowards compatibilty: already parsed
        return constraints

    constraints = {
        normalize_key(k): (
            normalize_list_value(v) if k in LIST_KEYS else
            normalize_value(v)
        ) for k, v in [s.split("=") for s in constraints.split(" ")]}

    return constraints


def normalize_key(key):
    key = key.strip()

    key = key.replace("-", "_")  # Our _client lib wants "_" in place of "-"

    # Convert camelCase to snake_case
    key = SNAKE1.sub(r'\1_\2', key)
    key = SNAKE2.sub(r'\1_\2', key).lower()

    return key


def normalize_value(value):
    value = value.strip()

    if MEM.match(value):
        # Translate aliases to Megabytes. e.g. 1G = 10240
        return int(value[:-1]) * FACTORS[value[-1:]]

    if value.isdigit():
        return int(value)

    return value


def normalize_list_value(value):
    values = value.strip().split(',')
    return [normalize_value(value) for value in values]


STORAGE = re.compile(
    '(?:(?:^|(?<=,))(?:|(?P<pool>[a-zA-Z]+[-?a-zA-Z0-9]*)|(?P<count>-?[0-9]+)|(?:(?P<size>-?[0-9]+(?:\\.[0-9]+)?)(?P<size_exp>[MGTPEZY])(?:i?B)?))(?:$|,))')


def parse_storage_constraint(constraint):
    storage = {'count': 1}
    for m in STORAGE.finditer(constraint):
        pool = m.group('pool')
        if pool:
            if 'pool' in storage:
                raise Exception("pool already specified")
            storage['pool'] = pool
        count = m.group('count')
        if count:
            count = int(count)
            storage['count'] = count if count > 0 else 1
        size = m.group('size')
        if size:
            storage['size'] = int(float(size) * FACTORS[m.group('size_exp')])
    return storage


DEVICE = re.compile(
    '^(?P<count>[0-9]+)?(?:^|,)(?P<type>[^,]+)(?:$|,(?!$))(?P<attrs>(?:[^=]+=[^;]+)+)*$')
ATTR = re.compile(';?(?P<key>[^=]+)=(?P<value>[^;]+)')


def parse_device_constraint(constraint):
    m = DEVICE.match(constraint)
    if m is None:
        raise Exception("device constraint does not match")
    device = {}
    count = m.group('count')
    if count:
        count = int(count)
        device['count'] = count if count > 0 else 1
    else:
        device['count'] = 1
    device['type'] = m.group('type')
    attrs = m.group('attrs')
    if attrs:
        device['attributes'] = {match.group('key'): match.group('value')
                                for match in ATTR.finditer(attrs)}
    return device
