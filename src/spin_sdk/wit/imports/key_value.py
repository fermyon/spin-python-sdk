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


# The set of errors which may be raised by functions in this interface
Error = Union[ErrorStoreTableFull, ErrorNoSuchStore, ErrorAccessDenied, ErrorOther]

class Store:
    """
    An open key-value store
    """
    
    @staticmethod
    def open(label: str) -> Any:
        """
        Open the store with the specified label.
        
        `label` must refer to a store allowed in the spin.toml manifest.
        
        `error::no-such-store` will be raised if the `label` is not recognized.
        """
        raise NotImplementedError

    def get(self, key: str) -> Optional[bytes]:
        """
        Get the value associated with the specified `key`
        
        Returns `ok(none)` if the key does not exist.
        """
        raise NotImplementedError

    def set(self, key: str, value: bytes) -> None:
        """
        Set the `value` associated with the specified `key` overwriting any existing value.
        """
        raise NotImplementedError

    def delete(self, key: str) -> None:
        """
        Delete the tuple with the specified `key`
        
        No error is raised if a tuple did not previously exist for `key`.
        """
        raise NotImplementedError

    def exists(self, key: str) -> int:
        """
        Return whether a tuple exists for the specified `key`
        """
        raise NotImplementedError

    def get_keys(self) -> List[str]:
        """
        Return a list of all the keys
        """
        raise NotImplementedError

    def drop(self):
        """
        Release this resource.
        """
        raise NotImplementedError



