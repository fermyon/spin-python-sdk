from spin_sdk import http, llm
from spin_sdk.http import Request, Response

class IncomingHandler(http.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        res = llm.infer("llama2-chat", "tell me a joke")
        print(res.text)
        print(res.usage)
        res = llm.infer_with_options("llama2-chat", "what is the theory of relativity", llm.InferencingParams(temperature=0.5))
        print(res.text)
        print(res.usage)
        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Hello from Python!", "utf-8")
        )
