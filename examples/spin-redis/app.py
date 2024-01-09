from spin_sdk.http import simple
from spin_sdk.http.simple import Request, Response
from spin_sdk import redis

class IncomingHandler(simple.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        db = redis.connect("redis://localhost:6379")
        print(db.get("test"))
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
