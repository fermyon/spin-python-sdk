from typing import TypeVar, Generic, Union, Optional, Union, Protocol, Tuple, List, Any, Self
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some



@dataclass
class ErrorInvalidAddress:
    pass


@dataclass
class ErrorTooManyConnections:
    pass


@dataclass
class ErrorTypeError:
    pass


@dataclass
class ErrorOther:
    value: str


Error = Union[ErrorInvalidAddress, ErrorTooManyConnections, ErrorTypeError, ErrorOther]
"""
Errors related to interacting with Redis
"""



@dataclass
class RedisParameterInt64:
    value: int


@dataclass
class RedisParameterBinary:
    value: bytes


RedisParameter = Union[RedisParameterInt64, RedisParameterBinary]
"""
A parameter type for the general-purpose `execute` function.
"""



@dataclass
class RedisResultNil:
    pass


@dataclass
class RedisResultStatus:
    value: str


@dataclass
class RedisResultInt64:
    value: int


@dataclass
class RedisResultBinary:
    value: bytes


RedisResult = Union[RedisResultNil, RedisResultStatus, RedisResultInt64, RedisResultBinary]
"""
A return type for the general-purpose `execute` function.
"""


class Connection:
    
    @classmethod
    def open(cls, address: str) -> Self:
        """
        Open a connection to the Redis instance at `address`.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.redis.Error)`
        """
        raise NotImplementedError

    def publish(self, channel: str, payload: bytes) -> None:
        """
        Publish a Redis message to the specified channel.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.redis.Error)`
        """
        raise NotImplementedError

    def get(self, key: str) -> Optional[bytes]:
        """
        Get the value of a key.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.redis.Error)`
        """
        raise NotImplementedError

    def set(self, key: str, value: bytes) -> None:
        """
        Set key to value.
        
        If key already holds a value, it is overwritten.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.redis.Error)`
        """
        raise NotImplementedError

    def incr(self, key: str) -> int:
        """
        Increments the number stored at key by one.
        
        If the key does not exist, it is set to 0 before performing the operation.
        An `error::type-error` is returned if the key contains a value of the wrong type
        or contains a string that can not be represented as integer.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.redis.Error)`
        """
        raise NotImplementedError

    def del_(self, keys: List[str]) -> int:
        """
        Removes the specified keys.
        
        A key is ignored if it does not exist. Returns the number of keys deleted.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.redis.Error)`
        """
        raise NotImplementedError

    def sadd(self, key: str, values: List[str]) -> int:
        """
        Add the specified `values` to the set named `key`, returning the number of newly-added values.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.redis.Error)`
        """
        raise NotImplementedError

    def smembers(self, key: str) -> List[str]:
        """
        Retrieve the contents of the set named `key`.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.redis.Error)`
        """
        raise NotImplementedError

    def srem(self, key: str, values: List[str]) -> int:
        """
        Remove the specified `values` from the set named `key`, returning the number of newly-removed values.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.redis.Error)`
        """
        raise NotImplementedError

    def execute(self, command: str, arguments: List[RedisParameter]) -> List[RedisResult]:
        """
        Execute an arbitrary Redis command and receive the result.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.redis.Error)`
        """
        raise NotImplementedError

    def __enter__(self):
        """Returns self"""
        return self
                                                                    
    def __exit__(self, *args):
        """
        Release this resource.
        """
        raise NotImplementedError



