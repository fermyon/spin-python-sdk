from spin_sdk.http import IncomingHandler
from spin_sdk.http import Request, Response
from spin_sdk import postgres

class IncomingHandler(IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        with postgres.open("user=postgres dbname=spin_dev host=127.0.0.1") as db:
            print(db.query("select * from test", []))
        
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
