import os

PYLIBJUJU_DEV_FEATURE_FLAG = "PYLIBJUJU_DEV_FEATURE_FLAGS"


DEFAULT_VALUES_FLAG = "default_values"


def feature_enabled(name):
    flags = os.environ.get(PYLIBJUJU_DEV_FEATURE_FLAG)
    if flags is not None:
        parts = [s.strip() for s in flags.split(",")]
        return name in parts
    return False
