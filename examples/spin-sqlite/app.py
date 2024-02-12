from spin_sdk.http import IncomingHandler
from spin_sdk.http import Request, Response
from spin_sdk import sqlite
from spin_sdk.wit.imports.sqlite import ValueInteger

class IncomingHandler(IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        with sqlite.open_default() as db:
            print(db.execute("SELECT * FROM todos WHERE id > (?);", [ValueInteger(1)]))
        
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
