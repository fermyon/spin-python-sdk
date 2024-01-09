from spin_sdk.wit.imports.mysql import Connection

def connect(connection_string: str) -> Connection:
    return Connection.open(connection_string)