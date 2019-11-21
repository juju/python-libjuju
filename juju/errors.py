class JujuError(Exception):
    def __init__(self, *args, **kwargs):
        self.message = ''
        self.errors = []
        if args:
            self.message = str(args[0])
            if isinstance(args[0], (list, tuple)):
                self.errors = args[0]
            elif len(args) > 1:
                self.errors = list(args)
            else:
                self.errors = [self.message]
        super().__init__(*args, **kwargs)


class JujuAPIError(JujuError):
    def __init__(self, result):
        self.result = result
        self.message = result['error']
        self.error_code = result.get('error-code')
        self.response = result['response']
        self.request_id = result['request-id']
        self.error_info = result['error-info'] if 'error-info' in result else None
        super().__init__(self.message)


class JujuConnectionError(ConnectionError, JujuError):
    pass


class JujuAuthError(JujuConnectionError):
    pass


class JujuRedirectException(Exception):
    """Exception indicating that a redirection was requested"""
    def __init__(self, redirect_info, follow_redirect=True):
        self.redirect_info = redirect_info
        self.follow_redirect = follow_redirect

    @property
    def ca_cert(self):
        return self.redirect_info['ca-cert']

    @property
    def endpoints(self):
        return [
            ('{value}:{port}'.format(**s), self.ca_cert)
            for servers in self.redirect_info['servers']
            for s in servers if s['scope'] == 'public' or not self.follow_redirect
        ]


class JujuEntityNotFoundError(JujuError):
    """Exception indicating that an entity was not found in the state. It was
       expected that the entity was found in state and this is a terminal
       condition.
       To fix this condition, you should disconnect and reconnect to ensure that
       any missing entities are correctly picked up."""
    def __init__(self, entity_name, entity_types=None):
        self.entity_name = entity_name
        self.entity_types = entity_types
        super().__init__("Entity not found: {}".format(entity_name))
