"""Module for interacting with a MySQL database"""

from spin_sdk.wit.imports.mysql import Connection

def opem(connection_string: str) -> Connection:
    """
    Open a connection with a MySQL database.
    
    The connection_string is the MySQL URL connection string.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.rdbms_types.ErrorConnectionFailed(str))` when a connection fails.
    
    A `spin_sdk.wit.types.Err(spin_sdk.wit.import.rdbms_types.ErrorOther(str))` when some other error occurs.
    """
    return Connection.open(connection_string)