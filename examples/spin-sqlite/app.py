from spin_sdk import http, sqlite
from spin_sdk.http import Request, Response
from spin_sdk.wit.imports.sqlite import ValueInteger

class IncomingHandler(http.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        with sqlite.open_default() as db:
            result = db.execute("SELECT * FROM todos WHERE id > (?);", [ValueInteger(1)])
            rows = result.rows
        
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes(str(rows), "utf-8")
        )
