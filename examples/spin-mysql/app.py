from spin_sdk import http, mysql
from spin_sdk.http import Request, Response

class IncomingHandler(http.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        with mysql.open("mysql://root:@127.0.0.1/spin_dev") as db:
            print(db.query("select * from test", []))
        
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
