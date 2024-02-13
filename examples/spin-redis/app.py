from spin_sdk.http import IncomingHandler, Request, Response
from spin_sdk import redis

class IncomingHandler(IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        with redis.open("redis://localhost:6379") as db:
            print(db.get("test"))
            
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
