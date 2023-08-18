# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

from .jasyncio import * # noqa

import warnings
warnings.warn('juju.loop module is being deprecated by 3.0, use juju.jasyncio instead')
