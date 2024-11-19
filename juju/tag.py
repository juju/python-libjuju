# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
from __future__ import annotations

# TODO: Tags should be a proper class, so that we can distinguish whether
# something is already a tag or not.  For example, 'user-foo' is a valid
# username, but is ambiguous with the already-tagged username 'foo'.


def _prefix(prefix: str, s: str) -> str:
    if s and not s.startswith(prefix):
        return f"{prefix}{s}"
    return s


def untag(prefix: str, s: str) -> str:
    if s and s.startswith(prefix):
        return s[len(prefix) :]
    return s


def cloud(cloud_name: str) -> str:
    return _prefix("cloud-", cloud_name)


def controller(controller_uuid: str) -> str:
    return _prefix("controller-", controller_uuid)


def credential(cloud: str, user: str, credential_name: str) -> str:
    credential_string = f"{cloud}_{user}_{credential_name}"
    return _prefix("cloudcred-", credential_string)


def model(model_uuid: str) -> str:
    return _prefix("model-", model_uuid)


def machine(machine_id: str) -> str:
    return _prefix("machine-", machine_id)


def user(username: str) -> str:
    return _prefix("user-", username)


def application(app_name: str) -> str:
    return _prefix("application-", app_name)


def storage(app_name: str) -> str:
    return _prefix("storage-", app_name)


def unit(unit_name: str) -> str:
    return _prefix("unit-", unit_name.replace("/", "-"))


def action(action_uuid: str) -> str:
    return _prefix("action-", action_uuid)


def space(space_name: str) -> str:
    return _prefix("space-", space_name)
