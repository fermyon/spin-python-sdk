"""Module for accessing Spin key-value stores"""

from spin_sdk.wit.imports.key_value import Store

def open(name: str) -> Store:
    """
    Open the store with the specified name.
  
    If `name` is "default", the default store is opened.  Otherwise, `name` must
    refer to a store defined and configured in a runtime configuration file
    supplied with the application.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.ErrorNoSuchStore)` will be raised if the `name` is not recognized.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.ErrorAccessDenied)` will be raised if the requesting component does not have
    access to the specified store.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.ErrorStoreTableFull)` will be raised if too many stores have been opened simultaneously.
    Closing one or more previously opened stores might address this using the `__exit__` method.
    
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.ErrorOther(str))` will be raised if some implementation specific error has occured (e.g I/O)
    """
    return Store.open(name)

def open_default() -> Store:
    """
    Open the default store.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.ErrorAccessDenied)`
    will be raised if the requesting component does not have access to the
    default store.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.ErrorStoreTableFull)` will be raised if too many stores have been opened simultaneously.
    Closing one or more previously opened stores might address this using the `__exit__` method.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.key_value.ErrorOther(str))` will be raised if some implementation specific error has occured (e.g I/O)
    """
    return Store.open("default")