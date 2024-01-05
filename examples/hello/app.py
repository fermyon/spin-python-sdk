from spin_sdk.http import simple
from spin_sdk.http.simple import Request, Response

class IncomingHandler(simple.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
