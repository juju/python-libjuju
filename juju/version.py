# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import pathlib
import re

import pathlib
import re

LTS_RELEASES = ["jammy", "focal", "bionic", "xenial", "trusty", "precise"]

DEFAULT_ARCHITECTURE = 'amd64'

# CLIENT_VERSION (that's read from the VERSION file) is the highest Juju server
# version that this client supports.
# Note that this is a ceiling. CLIENT_VERSION <= juju-controller-version works.
# For CLIENT_VERSION < juju-controller-version (strictly smaller), we emit a warning
# to update the client to the latest.
# However, for any CLIENT_VERSION > juju-controller-version, a "client incompatible
# with server" will be returned by the juju controller.
VERSION_FILE_PATH = pathlib.Path(__file__).parent.parent / 'VERSION'
CLIENT_VERSION = re.search(r'\d+\.\d+\.\d+', open(VERSION_FILE_PATH).read().strip()).group()
