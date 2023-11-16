"""Module for interacting with a Redis database"""

from collections.abc import Sequence

def redis_del(address: str, keys: Sequence[str]) -> int:
    """Removes the specified keys. A key is ignored if it does not exist."""
    raise NotImplementedError

def redis_get(address: str, key: str) -> bytes:
    """Get the value of a key."""
    raise NotImplementedError

def redis_incr(address: str, key: str) -> int:
    """Increments the number stored at key by one.

    If the key does not exist, it is set to 0 before performing the operation.

    An `AssertionError` is raised if the key contains a value of the wrong type
    or contains a string that can not be represented as integer.

    """
    raise NotImplementedError

def redis_publish(address: str, channel: str, payload: bytes):
    """Publish a Redis message to the specificed channel."""
    raise NotImplementedError

def redis_sadd(address: str, key: str, values: Sequence[str]) -> int:
    """Add the specified `values` to the set named `key`, returning the number of newly-added values."""
    raise NotImplementedError

def redis_set(address: str, key: str, value: bytes):
    """Set key to value. If key alreads holds a value, it is overwritten."""
    raise NotImplementedError

def redis_smembers(address: str, key: str) -> Sequence[str]:
    """ Retrieve the contents of the set named `key`."""
    raise NotImplementedError

def redis_srem(address: str, key: str, values: Sequence[str]) -> int:
    """Remove the specified `values` from the set named `key`, returning the number of newly-removed values."""
    raise NotImplementedError

def redis_execute(address: str, command: str, arguments: Sequence[int | bytes]) -> Sequence[int | bytes | str | None]:
    """Execute an arbitrary Redis command and receive the result."""    
    raise NotImplementedError
