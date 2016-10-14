
class JujuAPIError(Exception):
    def __init__(self, result):
        self.message = result['error']
        self.response = result['response']
        self.request_id = result['request-id']
        super().__init__(self.message)
