from spin_http import Response

def handle_request(request):
    print(f"Got request URI: {request.uri}")
    return Response(200, [("content-type", "text/plain")], f"Hello from Python! Got request URI: {request.uri}")
