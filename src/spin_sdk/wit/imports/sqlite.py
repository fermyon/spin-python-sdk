from typing import TypeVar, Generic, Union, Optional, Union, Protocol, Tuple, List, Any
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some


class Connection:
    """
    A handle to an open sqlite instance
    """
    
    @staticmethod
    def open(database: str) -> Connection:
        """
        Open a connection to a named database instance.
        
        If `database` is "default", the default instance is opened.
        
        `error::no-such-database` will be raised if the `name` is not recognized.
        """
        raise NotImplementedError

    def execute(self, statement: str, parameters: List[Value]) -> QueryResult:
        """
        Execute a statement returning back data if there is any
        """
        raise NotImplementedError

    def drop(self):
        (_, func, args, _) = self.finalizer.detach()
        self.handle = None
        func(args[0], args[1])



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


# The set of errors which may be raised by functions in this interface
Error = Union[ErrorNoSuchDatabase, ErrorAccessDenied, ErrorInvalidConnection, ErrorDatabaseFull, ErrorIo]


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


# A single column's result from a database query
Value = Union[ValueInteger, ValueReal, ValueText, ValueBlob, ValueNull]

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


