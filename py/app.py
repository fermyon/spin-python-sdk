from spin_http import Request, Response, send

def handle_request(request):
    print(f"Got request URI: {request.uri}")
    response = send(Request("GET", "https://some-random-api.ml/facts/dog", [], None))
    print(f"Got dog fact: {response.body}")
    return Response(200, [("content-type", "text/plain")], f"Hello from Python! Got request URI: {request.uri}")
