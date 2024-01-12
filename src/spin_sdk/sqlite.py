"""Module for interacting with an SQLite database"""

from typing import List
from spin_sdk.wit.imports.sqlite import Connection

def open(name: str) -> Connection:
    """Open a connection to a named database instance.

    If `database` is "default", the default instance is opened.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite(ErrorAccessDenied)` will be raised when the component does not have access to the specified database.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite(ErrorNoSuchDatabase)` will be raised when the host does not recognize the database name requested.
    
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite(ErrorInvalidConnection)` will be raised when the provided connection string is not valid.
    
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite(ErrorIo(str))` will be raised when implementation-specific error occured (e.g. I/O)
    """
    return Connection.open(name)

def open_default() -> Connection:
    """Open the default store.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite(ErrorAccessDenied)` will be raised when the component does not have access to the default database.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite(ErrorIo(str))` will be raised when implementation-specific error occured (e.g. I/O)
    """
    return Connection.open("default")