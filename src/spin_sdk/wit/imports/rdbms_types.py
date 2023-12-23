from typing import TypeVar, Generic, Union, Optional, Union, Protocol, Tuple, List, Any, Self
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some



@dataclass
class ErrorConnectionFailed:
    value: str


@dataclass
class ErrorBadParameter:
    value: str


@dataclass
class ErrorQueryFailed:
    value: str


@dataclass
class ErrorValueConversionFailed:
    value: str


@dataclass
class ErrorOther:
    value: str


# Errors related to interacting with a database.
Error = Union[ErrorConnectionFailed, ErrorBadParameter, ErrorQueryFailed, ErrorValueConversionFailed, ErrorOther]

class DbDataType(Enum):
    """
    Data types for a database column
    """
    BOOLEAN = 0
    INT8 = 1
    INT16 = 2
    INT32 = 3
    INT64 = 4
    UINT8 = 5
    UINT16 = 6
    UINT32 = 7
    UINT64 = 8
    FLOATING32 = 9
    FLOATING64 = 10
    STR = 11
    BINARY = 12
    OTHER = 13


@dataclass
class DbValueBoolean:
    value: int


@dataclass
class DbValueInt8:
    value: int


@dataclass
class DbValueInt16:
    value: int


@dataclass
class DbValueInt32:
    value: int


@dataclass
class DbValueInt64:
    value: int


@dataclass
class DbValueUint8:
    value: int


@dataclass
class DbValueUint16:
    value: int


@dataclass
class DbValueUint32:
    value: int


@dataclass
class DbValueUint64:
    value: int


@dataclass
class DbValueFloating32:
    value: float


@dataclass
class DbValueFloating64:
    value: float


@dataclass
class DbValueStr:
    value: str


@dataclass
class DbValueBinary:
    value: bytes


@dataclass
class DbValueDbNull:
    pass


@dataclass
class DbValueUnsupported:
    pass


# Database values
DbValue = Union[DbValueBoolean, DbValueInt8, DbValueInt16, DbValueInt32, DbValueInt64, DbValueUint8, DbValueUint16, DbValueUint32, DbValueUint64, DbValueFloating32, DbValueFloating64, DbValueStr, DbValueBinary, DbValueDbNull, DbValueUnsupported]


@dataclass
class ParameterValueBoolean:
    value: int


@dataclass
class ParameterValueInt8:
    value: int


@dataclass
class ParameterValueInt16:
    value: int


@dataclass
class ParameterValueInt32:
    value: int


@dataclass
class ParameterValueInt64:
    value: int


@dataclass
class ParameterValueUint8:
    value: int


@dataclass
class ParameterValueUint16:
    value: int


@dataclass
class ParameterValueUint32:
    value: int


@dataclass
class ParameterValueUint64:
    value: int


@dataclass
class ParameterValueFloating32:
    value: float


@dataclass
class ParameterValueFloating64:
    value: float


@dataclass
class ParameterValueStr:
    value: str


@dataclass
class ParameterValueBinary:
    value: bytes


@dataclass
class ParameterValueDbNull:
    pass


# Values used in parameterized queries
ParameterValue = Union[ParameterValueBoolean, ParameterValueInt8, ParameterValueInt16, ParameterValueInt32, ParameterValueInt64, ParameterValueUint8, ParameterValueUint16, ParameterValueUint32, ParameterValueUint64, ParameterValueFloating32, ParameterValueFloating64, ParameterValueStr, ParameterValueBinary, ParameterValueDbNull]

@dataclass
class Column:
    """
    A database column
    """
    name: str
    data_type: DbDataType

@dataclass
class RowSet:
    """
    A set of database rows
    """
    columns: List[Column]
    rows: List[List[DbValue]]


