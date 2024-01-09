from spin_sdk.wit.imports.postgres import Connection

def connect(connection_string: str) -> Connection:
    return Connection.open(connection_string)