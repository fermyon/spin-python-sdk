import numpy
import json
from spin_sdk.http import IncomingHandler, Request, Response

class IncomingHandler(IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        if request.method == "POST" \
           and request.uri == "/multiply" \
           and request.headers["content-type"] == "application/json" \
           and request.body is not None:
            [a, b] = json.loads(request.body)
            return Response(
                200,
                {"content-type": "application/json"},
                bytes(json.dumps(numpy.matmul(a, b).tolist()), "utf-8")
            )
        else:
            return Response(
                400,
                {"content-type": "text/plain"},
                bytes("Bad Request", "utf-8")
            )
