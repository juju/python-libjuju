
LTS_RELEASES = ["jammy", "focal", "bionic", "xenial", "trusty", "precise"]

DEFAULT_ARCHITECTURE = 'amd64'

# Juju server version we target. Depending on this value, the Juju server
# may stop the connecting considering us not compatible.
TARGET_JUJU_VERSION = '3.1-beta1'

# Used by connector to determine if we are compatible with the juju server
SUPPORTED_MINOR_VERSION = '3.1'
