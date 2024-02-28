from spin_sdk import http   
from spin_sdk.http import Request, Response

# Import the Router from the upstream project http_router
# See docs: https://github.com/klen/http-router
from http_router import Router

# This is the built-in URL parser.
from urllib.parse import urlparse, parse_qs

# You want the router declared outside of the handler function for scope.
# the trim_last_slash means that `/foo/` and `/foo` will be treated as the
# same.
router = Router(trim_last_slash=True)

@router.route("/")
def handle_index(uri, request):
    # Basic response for a basic request
    return Response(200, {"content-type": "text/plain"}, b"Hello World")


# Try this one with `curl -XPOST -d "TEST" localhost:3000/post`
@router.route("/post", methods=["POST"])
def handle_post(uri, request):
    # The post body is in `request.body`
    # Handle it however is appropriate. In this case,
    # we'll just echo it back
    return Response(200, {"content-type": "text/plain"}, request.body)


# Call this with curl localhost:3000/queryparams?foo=bar
@router.route("/queryparams")
def handle_queryparams(uri, request):
    # This is how to get query params out of URI
    params = parse_qs(uri.query)
    foo = params["foo"][0]
    # Echo back the value
    return Response(200, {"content-type": "text/plain"}, bytes(foo, "utf-8"))

class IncomingHandler(http.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        # I need to parse the URI because the Request object in Spin
        # is in the form /path/to/thing?param1=val1&p2=v2#anchor
        # and we need just /path/to/thing
        uri = urlparse(request.uri)
        handler = router(uri.path, request.method)

        # Now we have a handler that we can call.
        # Note that http_router handles 404 errors for us.
        return handler.target(uri, request)