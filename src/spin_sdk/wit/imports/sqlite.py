from typing import TypeVar, Generic, Union, Optional, Protocol, Tuple, List, Any, Self
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some



@dataclass
class Error_NoSuchDatabase:
    pass


@dataclass
class Error_AccessDenied:
    pass


@dataclass
class Error_InvalidConnection:
    pass


@dataclass
class Error_DatabaseFull:
    pass


@dataclass
class Error_Io:
    value: str


Error = Union[Error_NoSuchDatabase, Error_AccessDenied, Error_InvalidConnection, Error_DatabaseFull, Error_Io]
"""
The set of errors which may be raised by functions in this interface
"""



@dataclass
class Value_Integer:
    value: int


@dataclass
class Value_Real:
    value: float


@dataclass
class Value_Text:
    value: str


@dataclass
class Value_Blob:
    value: bytes


@dataclass
class Value_Null:
    pass


Value = Union[Value_Integer, Value_Real, Value_Text, Value_Blob, Value_Null]
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



