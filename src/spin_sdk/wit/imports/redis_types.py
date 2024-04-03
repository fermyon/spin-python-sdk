from typing import TypeVar, Generic, Union, Optional, Protocol, Tuple, List, Any, Self
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some


class Error(Enum):
    """
    General purpose error.
    """
    SUCCESS = 0
    ERROR = 1


@dataclass
class RedisParameter_Int64:
    value: int


@dataclass
class RedisParameter_Binary:
    value: bytes


RedisParameter = Union[RedisParameter_Int64, RedisParameter_Binary]
"""
A parameter type for the general-purpose `execute` function.
"""



@dataclass
class RedisResult_Nil:
    pass


@dataclass
class RedisResult_Status:
    value: str


@dataclass
class RedisResult_Int64:
    value: int


@dataclass
class RedisResult_Binary:
    value: bytes


RedisResult = Union[RedisResult_Nil, RedisResult_Status, RedisResult_Int64, RedisResult_Binary]
"""
A return type for the general-purpose `execute` function.
"""



