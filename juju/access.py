# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from .errors import JujuNotValid

# No permissions at all
NO_ACCESS = ""

# Model permissions

READ_ACCESS = "read"
WRITE_ACCESS = "write"
CONSUME_ACCESS = "consume"
ADMIN_ACCESS = "admin"
MODEL_ACCESS_LEVELS = {READ_ACCESS, WRITE_ACCESS, CONSUME_ACCESS, ADMIN_ACCESS}

# Controller permissions

LOGIN_ACCESS = "login"
ADD_MODEL_ACCESS = "add-model"
SUPERUSER_ACCESS = "superuser"
CONTROLLER_ACCESS_LEVELS = {LOGIN_ACCESS, ADD_MODEL_ACCESS, SUPERUSER_ACCESS}

OFFER_ACCESS_LEVELS = {READ_ACCESS, CONSUME_ACCESS, ADMIN_ACCESS}

ALL_ACCESS_LEVELS = MODEL_ACCESS_LEVELS.union(CONTROLLER_ACCESS_LEVELS)


def validate_access_level(access):
    if access not in ALL_ACCESS_LEVELS:
        raise JujuNotValid("access level", access)


def validate_offer_access(access):
    validate_access_level()
    if access not in OFFER_ACCESS_LEVELS:
        raise JujuNotValid("offer access level", access)


def validate_model_access(access):
    validate_access_level(access)
    if access not in MODEL_ACCESS_LEVELS:
        raise JujuNotValid("model access level", access)


def validate_controller_access(access):
    validate_access_level(access)
    if access not in CONTROLLER_ACCESS_LEVELS:
        raise JujuNotValid("controller access level", access)
