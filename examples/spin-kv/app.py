from spin_sdk.http import simple
from spin_sdk.http.simple import Request, Response
from spin_sdk import key_value

class IncomingHandler(simple.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        a = key_value.open_default()
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