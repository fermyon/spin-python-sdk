from typing import TypeVar, Generic, Union, Optional, Union, Protocol, Tuple, List, Any, Self
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



