class JujuError(Exception):
    pass


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
