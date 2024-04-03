"""Module for interacting with an SQLite database"""

from typing import List
from spin_sdk.wit.imports.sqlite import Connection, Value_Integer, Value_Real, Value_Text, Value_Blob

def open(name: str) -> Connection:
    """Open a connection to a named database instance.

    If `database` is "default", the default instance is opened.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite.Error_AccessDenied)` will be raised when the component does not have access to the specified database.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite.Error_NoSuchDatabase)` will be raised when the host does not recognize the database name requested.
    
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite.Error_InvalidConnection)` will be raised when the provided connection string is not valid.
    
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite.Error_Io(str))` will be raised when implementation-specific error occured (e.g. I/O)
    """
    return Connection.open(name)

def open_default() -> Connection:
    """Open the default store.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite.Error_AccessDenied)` will be raised when the component does not have access to the default database.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.sqlite.Error_Io(str))` will be raised when implementation-specific error occured (e.g. I/O)
    """
    return Connection.open("default")
