from spin_sdk.http import simple
from spin_sdk.http.simple import Request, Response
from spin_sdk import sqlite
from spin_sdk.wit.imports.sqlite import ValueInteger

class IncomingHandler(simple.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        db = sqlite.open_default()
        print(db.execute("SELECT * FROM todos WHERE id > (?);", [ValueInteger(1)]))
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
