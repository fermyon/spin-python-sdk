from spin_http import Response
from spin_redis import redis_del, redis_get, redis_incr, redis_set, redis_sadd, redis_srem, redis_smembers, redis_execute
from spin_config import config_get


def handle_request(request):

    redis_address = config_get("redis_address")
    redis_set(redis_address, "foo", b"bar")
    value = redis_get(redis_address, "foo")
    redis_del(redis_address, ["testIncr"])
    redis_incr(redis_address, "testIncr")

    redis_sadd(redis_address, "testSets", ["hello", "world"])
    content = redis_smembers(redis_address, "testSets")
    redis_srem(redis_address, "testSets", ["hello"])
    redis_execute(redis_address, "set", [b"foo", b"hello"])
    redis_execute(redis_address, "append", [b"foo", b", world!"])

    assert value == b"bar", f"expected \"bar\", got \"{str(value, 'utf-8')}\""

    return Response(200,
                    [("content-type", "text/plain")],
                    bytes(f"Executed outbound Redis commands", "utf-8"))
