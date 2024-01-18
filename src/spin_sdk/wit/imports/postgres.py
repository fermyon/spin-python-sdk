from typing import TypeVar, Generic, Union, Optional, Union, Protocol, Tuple, List, Any, Self
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some
from ..imports import rdbms_types

class Connection:
    """
    A connection to a postgres database.
    """
    
    @classmethod
    def open(cls, address: str) -> Self:
        """
        Open a connection to the Postgres instance at `address`.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.rdbms_types.Error)`
        """
        raise NotImplementedError

    def query(self, statement: str, params: List[rdbms_types.ParameterValue]) -> rdbms_types.RowSet:
        """
        Query the database.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.rdbms_types.Error)`
        """
        raise NotImplementedError

    def execute(self, statement: str, params: List[rdbms_types.ParameterValue]) -> int:
        """
        Execute command to the database.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.rdbms_types.Error)`
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



