from spin_http import Request, Response, http_send
from spin_redis import redis_get, redis_set
from spin_config import config_get
from os import environ
import toml

def handle_request(request):
    print(f"Got request URI: {request.uri}")

    print(f"Here's my environment: {environ}")

    some_toml = """
    title = "foo"

    [bar]
    baz = "wow"
    such = "toml"
    """

    print(f"And here's some TOML: {toml.loads(some_toml)}")

    response = http_send(Request("GET", "https://some-random-api.ml/facts/dog", [], None))
    print(f"Got dog fact: {str(response.body, 'utf-8')}")

    redis_address = config_get("redis_address")
    redis_set(redis_address, "foo", b"bar")
    value = redis_get(redis_address, "foo")
    assert value == b"bar", f"expected \"bar\", got \"{str(value, 'utf-8')}\""

    return Response(200,
                    [("content-type", "text/plain")],
                    bytes(f"Hello from Python! Got request URI: {request.uri}", "utf-8"))
