import logging

from . import model
from .errors import JujuEntityNotFoundError

log = logging.getLogger(__name__)


class Endpoint:
    def __init__(self, model, data):
        self.model = model
        self.data = data

    def __repr__(self):
        return '<Endpoint {}:{}>'.format(self.data['application-name'], self.name)

    @property
    def application_name(self):
        return self.data['application-name']

    @property
    def application(self):
        """Application returns the underlying application model from the state.
        If no application is found, then a JujuEntityNotFoundError is raised, in
        this scenario it is expected that you disconnect and reconnect to the
        model.
        """
        app_name = self.data['application-name']
        if app_name in self.model.applications:
            return self.model.applications[app_name]
        raise JujuEntityNotFoundError(app_name, ["application"])

    @property
    def name(self):
        return self.data['relation']['name']

    @property
    def interface(self):
        return self.data['relation']['interface']

    @property
    def role(self):
        return self.data['relation']['role']

    @property
    def scope(self):
        return self.data['relation']['scope']


class Relation(model.ModelEntity):
    def __repr__(self):
        return '<Relation id={} {}>'.format(self.entity_id, self.key)

    @property
    def endpoints(self):
        return [Endpoint(self.model, data)
                for data in self.safe_data['endpoints']]

    @property
    def provides(self):
        """
        The endpoint on the provides side of this relation, or None.
        """
        for endpoint in self.endpoints:
            if endpoint.role == 'provider':
                return endpoint
        return None

    @property
    def requires(self):
        """
        The endpoint on the requires side of this relation, or None.
        """
        for endpoint in self.endpoints:
            if endpoint.role == 'requirer':
                return endpoint
        return None

    @property
    def peers(self):
        """
        The peers endpoint of this relation, or None.
        """
        for endpoint in self.endpoints:
            if endpoint.role == 'peer':
                return endpoint
        return None

    @property
    def is_subordinate(self):
        return any(ep.scope == 'container' for ep in self.endpoints)

    @property
    def is_peer(self):
        return any(ep.role == 'peer' for ep in self.endpoints)

    def matches(self, *specs):
        """
        Check if this relation matches relationship specs.

        Relation specs are strings that would be given to Juju to establish a
        relation, and should be in the form ``<application>[:<endpoint_name>]``
        where the ``:<endpoint_name>`` suffix is optional.  If the suffix is
        omitted, this relation will match on any endpoint as long as the given
        application is involved.

        In other words, this relation will match a spec if that spec could have
        created this relation.

        :return: True if all specs match.
        """
        # Matches expects that the underlying application exists when it walks
        # over the endpoints.
        # This isn't directly required, but it validates that the framework
        # has all the information available to it, when you walk over all the
        # relations.
        # The one exception is remote-<uuid> applications aren't real
        # applications in the general sense of a application, but are more akin
        # to a shadow application.
        def model_application_exists(app_name):
            model_app_name = None
            if app_name in self.model.applications:
                model_app_name = self.model.applications[app_name].name
            elif app_name in self.model.remote_applications:
                model_app_name = self.model.remote_applications[app_name].name
            elif app_name in self.model.application_offers:
                model_app_name = self.model.application_offers[app_name].name
            return model_app_name == app_name

        for spec in specs:
            if ':' in spec:
                app_name, endpoint_name = spec.split(':')
            else:
                app_name, endpoint_name = spec, None
            for endpoint in self.endpoints:
                if app_name == endpoint.application_name and \
                   model_application_exists(app_name) and \
                   endpoint_name in (endpoint.name, None):
                    # found a match for this spec, so move to next one
                    break
            else:
                # no match for this spec
                return False
        return True

    @property
    def applications(self):
        """
        All applications involved in this relation.
        """
        return [ep.application for ep in self.endpoints]

    async def destroy(self):
        raise NotImplementedError()
        # TODO: destroy a relation
