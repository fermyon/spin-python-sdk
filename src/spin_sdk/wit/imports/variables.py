from typing import TypeVar, Generic, Union, Optional, Union, Protocol, Tuple, List, Any, Self
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some



@dataclass
class ErrorInvalidName:
    value: str


@dataclass
class ErrorUndefined:
    value: str


@dataclass
class ErrorProvider:
    value: str


@dataclass
class ErrorOther:
    value: str


# The set of errors which may be raised by functions in this interface.
Error = Union[ErrorInvalidName, ErrorUndefined, ErrorProvider, ErrorOther]


def get(name: str) -> str:
    """
    Get an application variable value for the current component.
    
    The name must match one defined in in the component manifest.
    """
    raise NotImplementedError

