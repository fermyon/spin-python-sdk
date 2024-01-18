from spin_sdk.http import simple
from spin_sdk.http.simple import Request, Response
from spin_sdk import mysql

class IncomingHandler(simple.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        with mysql.open("mysql://root:@127.0.0.1/spin_dev") as db:
            print(db.query("select * from test", []))
        
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
