from typing import TypeVar, Generic, Union, Optional, Union, Protocol, Tuple, List, Any, Self
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some



@dataclass
class ErrorNoSuchDatabase:
    pass


@dataclass
class ErrorAccessDenied:
    pass


@dataclass
class ErrorInvalidConnection:
    pass


@dataclass
class ErrorDatabaseFull:
    pass


@dataclass
class ErrorIo:
    value: str


Error = Union[ErrorNoSuchDatabase, ErrorAccessDenied, ErrorInvalidConnection, ErrorDatabaseFull, ErrorIo]
"""
The set of errors which may be raised by functions in this interface
"""



@dataclass
class ValueInteger:
    value: int


@dataclass
class ValueReal:
    value: float


@dataclass
class ValueText:
    value: str


@dataclass
class ValueBlob:
    value: bytes


@dataclass
class ValueNull:
    pass


Value = Union[ValueInteger, ValueReal, ValueText, ValueBlob, ValueNull]
"""
A single column's result from a database query
"""


@dataclass
class RowResult:
    """
    A set of values for each of the columns in a query-result
    """
    values: List[Value]

@dataclass
class QueryResult:
    """
    A result of a query
    """
    columns: List[str]
    rows: List[RowResult]

class Connection:
    """
    A handle to an open sqlite instance
    """
    
    @classmethod
    def open(cls, database: str) -> Self:
        """
        Open a connection to a named database instance.
        
        If `database` is "default", the default instance is opened.
        
        `error::no-such-database` will be raised if the `name` is not recognized.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite.Error)`
        """
        raise NotImplementedError

    def execute(self, statement: str, parameters: List[Value]) -> QueryResult:
        """
        Execute a statement returning back data if there is any
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite.Error)`
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



