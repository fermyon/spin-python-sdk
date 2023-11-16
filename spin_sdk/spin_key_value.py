"""Module for accessing Spin key-value stores"""

from collections.abc import Sequence
from typing import Optional

class Store:
    """Represents an open key-value store"""
    
    def get(self, key: str) -> Optional[bytes]:
        """Get the value associated with the specified `key` from the specified `store`,
        or `None` if no such value exists.

        """
        raise NotImplementedError

    def set(self, key: str, value: bytes):
        """Set the `value` associated with the specified `key` in the specified `store`,
        overwriting any existing value.

        """
        raise NotImplementedError

    def delete(self, key: str):
        """Delete the tuple with the specified `key` from the specified `store`, if it
        exists.

        """
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        """Return whether a tuple exists for the specified `key` in the specified
        `store`.

        """
        raise NotImplementedError

    def get_keys(self) -> Sequence[str]:
        """Return a list of all the keys in the specified `store`."""
        raise NotImplementedError        
    
def kv_open(name: str) -> Store:
    """Open the store with the specified name.
  
    If `name` is "default", the default store is opened.  Otherwise, `name` must
    refer to a store defined and configured in a runtime configuration file
    supplied with the application.

    An `AssertionError` will be raised if the `name` is not recognized or the
    requesting component does not have access to the specified store.

    """
    raise NotImplementedError
    
def kv_open_default() -> Store:
    """Open the default store.

    An `AssertionError` will be raised if the requesting component does not have
    access to the specified store.

    """
    raise NotImplementedError
