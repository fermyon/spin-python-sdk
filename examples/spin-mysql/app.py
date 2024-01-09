from spin_sdk.http import simple
from spin_sdk.http.simple import Request, Response
from spin_sdk import mysql

class IncomingHandler(simple.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        db = mysql.connect("mysql://root:@127.0.0.1/spin_dev")
        print(db.query("select * from test", []))
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
