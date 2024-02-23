"""Module for interacting with Spin Variables"""

from spin_sdk.wit.imports import variables

def get(key: str):
    """
    Gets the value of the given key
    """
    return variables.get(key)
