# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import logging

from . import model, tag

log = logging.getLogger(__name__)


class RemoteApplication(model.ModelEntity):

    @property
    def status(self):
        """Get the application status, as set by the charm's leader.

        """
        return self.safe_data['status']['current']

    @property
    def status_message(self):
        """Get the application status message, as set by the charm's leader.

        """
        return self.safe_data['status']['message']

    @property
    def tag(self):
        return tag.application(self.name)


class ApplicationOffer(model.ModelEntity):
    @property
    def tag(self):
        return tag.application(self.name)

    @property
    def offer_name(self):
        return self.safe_data['offer-name']

    @property
    def application_name(self):
        return self.safe_data['application-name']
