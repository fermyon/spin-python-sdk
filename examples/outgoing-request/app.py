from spin_sdk.http import simple
from spin_sdk.http.simple import Request, Response, send

class IncomingHandler(simple.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        try:
            url = request.headers["url"]
        except KeyError:
            return Response(
                400,
                {"content-type": "text/plain"},
                bytes("Please specify `url` header", "utf-8")
            )

        return send(Request("GET", url, {}, None))
