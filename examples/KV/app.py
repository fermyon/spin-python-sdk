from spin_http import Response
from spin_key_value import kv_open_default


def handle_request(request):

    store = kv_open_default()

    match request.method:
        case "GET":
            value = store.get(request.uri)
            return Response(200, [("content-type", "text/plain")], value)
        case "POST":
            store.set(request.uri, request.body)
            return Response(200, [("content-type", "text/plain")])
        case "DELETE":
            store.delete(request.uri)
            return Response(200, [("content-type", "text/plain")])
        case "HEAD":
            if store.exists(request.uri):
                return Response(200, [("content-type", "text/plain")])
            return Response(404, [("content-type", "text/plain")])
        case default:
            return Response(405, [("content-type", "text/plain")])
