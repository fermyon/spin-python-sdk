from typing import List
from spin_sdk.wit.imports.sqlite import Connection

def open(name: str) -> Connection:
    return Connection.open(name)

def open_default() -> Connection:
    return Connection.open("default")