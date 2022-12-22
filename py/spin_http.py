class Request:
    def __init__(self, method, uri, headers, body):
        self.method = method
        self.uri = uri
        self.headers = headers
        self.body = body

class Response:
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body
