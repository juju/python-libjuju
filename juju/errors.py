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
        super().__init__(self.message)


class JujuConnectionError(ConnectionError, JujuError):
    pass
