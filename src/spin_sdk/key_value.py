from spin_sdk.wit.imports.key_value import Store

def open(name: str) -> Store:
    return Store.open(name)

def open_default() -> Store:
    return Store.open("default")