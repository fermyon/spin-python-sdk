"""Module for interacting with a Postgres database"""

from spin_sdk.wit.imports.postgres import Connection

def open(connection_string: str) -> Connection:
    """
    Open a connection with a Postgres database.
    
    The connection_string is the Postgres URL connection string.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.postgres(ErrorConnectionFailed(str))` when a connection fails.
    
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.postgres(ErrorOther(str))` when some other error occurs.
    """
    return Connection.open(connection_string)