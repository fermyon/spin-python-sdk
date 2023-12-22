from typing import TypeVar, Generic, Union, Optional, Union, Protocol, Tuple, List, Any
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some



@dataclass
class ErrorSuccess:
    pass


@dataclass
class ErrorError:
    pass


Error = Union[ErrorSuccess, ErrorError]

