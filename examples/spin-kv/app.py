from spin_sdk.http import IncomingHandler
from spin_sdk.http import Request, Response
from spin_sdk import key_value

class IncomingHandler(IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        with key_value.open_default() as a:
            a.set("test", bytes("hello world!", "utf-8"))
            print(a.get_keys())
            print(a.exists("test"))
            print(a.get("test"))
            a.delete("test")
            print(a.get_keys())
            
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
