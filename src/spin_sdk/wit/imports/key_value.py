from typing import TypeVar, Generic, Union, Optional, Union, Protocol, Tuple, List, Any, Self
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some



@dataclass
class ErrorStoreTableFull:
    pass


@dataclass
class ErrorNoSuchStore:
    pass


@dataclass
class ErrorAccessDenied:
    pass


@dataclass
class ErrorOther:
    value: str


Error = Union[ErrorStoreTableFull, ErrorNoSuchStore, ErrorAccessDenied, ErrorOther]
"""
The set of errors which may be raised by functions in this interface
"""


class Store:
    """
    An open key-value store
    """
    
    @classmethod
    def open(cls, label: str) -> Self:
        """
        Open the store with the specified label.
        
        `label` must refer to a store allowed in the spin.toml manifest.
        
        `error::no-such-store` will be raised if the `label` is not recognized.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.Error)`
        """
        raise NotImplementedError

    def get(self, key: str) -> Optional[bytes]:
        """
        Get the value associated with the specified `key`
        
        Returns `ok(none)` if the key does not exist.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.Error)`
        """
        raise NotImplementedError

    def set(self, key: str, value: bytes) -> None:
        """
        Set the `value` associated with the specified `key` overwriting any existing value.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.Error)`
        """
        raise NotImplementedError

    def delete(self, key: str) -> None:
        """
        Delete the tuple with the specified `key`
        
        No error is raised if a tuple did not previously exist for `key`.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.Error)`
        """
        raise NotImplementedError

    def exists(self, key: str) -> int:
        """
        Return whether a tuple exists for the specified `key`
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.Error)`
        """
        raise NotImplementedError

    def get_keys(self) -> List[str]:
        """
        Return a list of all the keys
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.Error)`
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



