#!/usr/bin/env python3
# Copyright 2023 jtirado
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

https://discourse.charmhub.io/t/4208
"""

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus

# Log messages can be retrieved using juju debug-log
logger = logging.getLogger(__name__)


class CharmSecretCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)

        self.framework.observe(self.on.install, self._on_install_create_secret)

    def _on_install_create_secret(self, event):
        """Create a secret to play with."""
        content = {
            'username': 'useradmin',
            'password': '1234',
        }
        secret = self.app.add_secret(content)
        logger.info("created secret %s", secret)
        self.unit.status = ActiveStatus()


if __name__ == "__main__":  # pragma: nocover
    main(CharmSecretCharm)
