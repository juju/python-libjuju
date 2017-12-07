import logging

from . import model

log = logging.getLogger(__name__)


class Endpoint:
    def __init__(self, model, data):
        self.model = model
        self.data = data

    def __repr__(self):
        return '<Endpoint {}:{}>'.format(self.application.name, self.name)

    @property
    def application(self):
        return self.model.applications[self.data['application-name']]

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
        for spec in specs:
            if ':' in spec:
                app_name, endpoint_name = spec.split(':')
            else:
                app_name, endpoint_name = spec, None
            for endpoint in self.endpoints:
                if app_name == endpoint.application.name and \
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
