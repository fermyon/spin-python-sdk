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

    if request.uri == "/duplicateheadertest":
        test_headers = [("spin-header-test-key1", "value1"), ("spin-header-test-key2", "value2"),
                        ("spin-header-test-key1", "value3"), ("spin-header-test-key2", "value4")]

        key1_test_passes = request.headers.get(
            "spin-header-test-key1") == "value1, value3"
        key2_test_passes = request.headers.get(
            "spin-header-test-key2") == "value2, value4"
        if key1_test_passes and key2_test_passes:
            response_content = "Duplicate Header Name Test: Pass"
            response_code = 200

        else:
            example_curl_headers = '-H "spin-header-test-key1: value1" -H "spin-header-test-key2: value2" -H "spin-header-test-key1: value3" -H "spin-header-test-key2: value4"'
            example_curl_request = f'curl {example_curl_headers} http://127.0.0.1:3000/duplicateheadertest'
            required_headers = "\n".join(
                [str(header) for header in test_headers])
            response_content = f"""
---------------------- Duplicate Header Name Test -------------------------------------
To make this test pass, you must include the following headers in your request:
{required_headers}

Example Passing Curl Request: {example_curl_request}

Actual Headers Received:
{request.headers}
---------------------------------------------------------------------------------------
"""
            response_code = 404

        return Response(response_code, {"content-type": "text/plain"}, bytes(response_content, "utf-8"))

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
