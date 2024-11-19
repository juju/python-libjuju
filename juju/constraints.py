# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

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
from typing import Dict, List, Optional, TypedDict, Union

from typing_extensions import NotRequired, Required

# Matches on a string specifying memory size
MEM = re.compile("^[1-9][0-9]*[MGTP]$")

# Multiplication factors to get Megabytes
# https://github.com/juju/juju/blob/master/constraints/constraints.go#L666
FACTORS = {
    "M": 1024**0,
    "G": 1024**1,
    "T": 1024**2,
    "P": 1024**3,
    "E": 1024**4,
    "Z": 1024**5,
    "Y": 1024**6,
}

# List of supported constraint keys, see
# http://github.com/cderici/juju/blob/2.9/core/constraints/constraints.go#L20-L39
SUPPORTED_KEYS = [
    "arch",
    "container",
    "cpu_cores",
    "cores",
    "cpu_power",
    "mem",
    "root_disk",
    "root_disk_source",
    "tags",
    "instance_role",
    "instance_type",
    "spaces",
    "virt_type",
    "zones",
    "allocate_public_ip",
]

LIST_KEYS = {"tags", "spaces", "zones"}

SNAKE1 = re.compile(r"(.)([A-Z][a-z]+)")
SNAKE2 = re.compile("([a-z0-9])([A-Z])")


ParsedValue = Union[int, bool, str]


class ConstraintsDict(TypedDict, total=False):
    allocate_public_ip: ParsedValue
    arch: ParsedValue
    container: ParsedValue
    cores: ParsedValue
    cpu_cores: ParsedValue
    cpu_power: ParsedValue
    instance_role: ParsedValue
    instance_type: ParsedValue
    mem: ParsedValue
    root_disk: ParsedValue
    root_dist_source: ParsedValue
    spaces: List[ParsedValue]
    tags: List[ParsedValue]
    virt_type: ParsedValue
    zones: List[ParsedValue]


def parse(constraints: Union[str, ConstraintsDict]) -> Optional[ConstraintsDict]:
    """Constraints must be expressed as a string containing only spaces
    and key value pairs joined by an '='.

    """
    if not constraints:
        return None

    if isinstance(constraints, dict):
        # Forwards compatibility: already parsed
        return constraints

    normalized_constraints: ConstraintsDict = {}
    for s in constraints.split(" "):
        if "=" not in s:
            raise ValueError("malformed constraint %s" % s)

        k, v = s.split("=")
        normalized_constraints[normalize_key(k)] = (
            normalize_list_value(v) if k in LIST_KEYS else normalize_value(v)
        )

    return normalized_constraints


def normalize_key(orig_key: str) -> str:
    key = orig_key.strip()

    key = key.replace("-", "_")  # Our _client lib wants "_" in place of "-"

    # Convert camelCase to snake_case
    key = SNAKE1.sub(r"\1_\2", key)
    key = SNAKE2.sub(r"\1_\2", key).lower()

    if key not in SUPPORTED_KEYS:
        raise ValueError("unknown constraint in %s" % orig_key)
    return key


def normalize_value(value: str) -> Union[int, bool, str]:
    value = value.strip()

    if MEM.match(value):
        # Translate aliases to Megabytes. e.g. 1G = 10240
        return int(value[:-1]) * FACTORS[value[-1:]]

    if value.isdigit():
        return int(value)

    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    return value


def normalize_list_value(value: str) -> List[ParsedValue]:
    values = value.strip().split(",")
    return [normalize_value(value) for value in values]


STORAGE = re.compile(
    # original regex:
    # '(?:(?:^|(?<=,))(?:|(?P<pool>[a-zA-Z]+[-?a-zA-Z0-9]*)|(?P<count>-?[0-9]+)|(?:(?P<size>-?[0-9]+(?:\\.[0-9]+)?)(?P<size_exp>[MGTPEZY])(?:i?B)?))(?:$|,))'
    # with formatting and explanation -- note that this regex is used with re.finditer:
    "(?:"
    "(?:^|(?<=,))"  # start of string or previous match ends with ','
    "(?:"  # match one of the following:
    "|(?P<pool>[a-zA-Z]+[-?a-zA-Z0-9]*)"  # * pool: a sequence starting with a letter, ending with a letter or number,
    # ------- and including letters, numbers and hyphens (no more than one in a row)
    "|(?P<count>-?[0-9]+)"  # * count: an optional minus sign followed by one or more digits
    "|(?:"  # * size (number) and size_exp (units):
    "(?P<size>-?[0-9]+(?:\\.[0-9]+)?)"  # -- * an optional minus sign followed by one or more digits, optionally with decimal point and more digits
    "(?P<size_exp>[MGTPEZY])(?:i?B)?)"  # -- * one of MGTPEZY, optionally followed by iB or B, for example 1M or 2.0MB or -3.3MiB
    ")"
    "(?:$|,)"  # end of string or ','
    ")"
)


class StorageConstraintDict(TypedDict):
    count: Required[int]  # >= 1
    pool: NotRequired[str]
    size: NotRequired[int]


def parse_storage_constraint(constraint: str) -> StorageConstraintDict:
    storage: StorageConstraintDict = {"count": 1}
    for m in STORAGE.finditer(constraint):
        pool = m.group("pool")
        if pool:
            if "pool" in storage:
                raise ValueError("pool already specified")
            storage["pool"] = pool
        count = m.group("count")
        if count:
            count = int(count)
            storage["count"] = count if count > 0 else 1
        size = m.group("size")
        if size:
            storage["size"] = int(float(size) * FACTORS[m.group("size_exp")])
    return storage


DEVICE = re.compile(
    # original regex:
    # '^(?P<count>[0-9]+)?(?:^|,)(?P<type>[^,]+)(?:$|,(?!$))(?P<attrs>(?:[^=]+=[^;]+)+)*$'
    # with formatting and explanation -- note this regex is used with re.match:
    "^"  # start of string
    "(?P<count>[0-9]+)?"  # count is 1+ digits, and is optional
    "(?:^|,)"  # match start of string or a comma
    # -- so type can be at the start or comma separated from count
    "(?P<type>[^,]+)"  # type is 1+ anything not a comma (including digits), and is required
    "(?:$|,(?!$))"  # match end of string | or a non-trailing comma
    # -- so type can be at the end or followed by attrs
    "(?P<attrs>(?:[^=]+=[^;]+)+)*"  # attrs is any number of semicolon separated key=value items
    # -- value can have spare '=' inside, possible not intended
    # -- attrs will be matched with ATTR.finditer afterwards in parse_device_constraint
    "$"  # end of string
)
ATTR = re.compile(";?(?P<key>[^=]+)=(?P<value>[^;]+)")


class DeviceConstraintDict(TypedDict):
    count: Required[int]
    type: Required[str]
    attributes: NotRequired[Dict[str, str]]


def parse_device_constraint(constraint: str) -> DeviceConstraintDict:
    m = DEVICE.match(constraint)
    if m is None:
        raise ValueError("device constraint does not match")
    device: DeviceConstraintDict = {}
    count = m.group("count")
    if count:
        count = int(count)
        device["count"] = count if count > 0 else 1
    else:
        device["count"] = 1
    device["type"] = m.group("type")
    attrs = m.group("attrs")
    if attrs:
        device["attributes"] = {
            match.group("key"): match.group("value") for match in ATTR.finditer(attrs)
        }
    return device
