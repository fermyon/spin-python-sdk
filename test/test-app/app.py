from spin_http import Request, Response, http_send
from spin_redis import redis_del, redis_get, redis_incr, redis_set, redis_sadd, redis_srem, redis_smembers
from spin_config import config_get
from os import environ
import toml

def handle_request(request):
    if request.uri == "/foo":
        return Response(200,
                        {"content-type": "text/plain"},
                        bytes(f"foo indeed", "utf-8"))

    print(f"Got request URI: {request.uri}")

    print(f"Here's my environment: {environ}")

    some_toml = """
    title = "foo"

    [bar]
    baz = "wow"
    such = "toml"
    """
    print(f"And here's some TOML: {toml.loads(some_toml)}")

    my_file = open("/foo.txt", "r")
    print(f"And here's the content of foo.txt: {my_file.read()}")

    response = http_send(Request("GET", "http://localhost:3000/foo", {}, None))
    print(f"Got foo: {str(response.body, 'utf-8')}")

    return Response(200,
                    {"content-type": "text/plain"},
                    bytes(f"Hello from Python! Got request URI: {request.uri}", "utf-8"))
