from spin_sdk.http import simple
from spin_sdk.http.simple import Request, Response
from spin_sdk import postgres

class IncomingHandler(simple.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        db = postgres.connect("user=postgres dbname=spin_dev host=127.0.0.1")
        print(db.query("select * from test", []))
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
