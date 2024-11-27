"""
A keyvalue interface that provides batch operations.

A batch operation is an operation that operates on multiple keys at once.

Batch operations are useful for reducing network round-trip time. For example, if you want to
get the values associated with 100 keys, you can either do 100 get operations or you can do 1
batch get operation. The batch operation is faster because it only needs to make 1 network call
instead of 100.

A batch operation does not guarantee atomicity, meaning that if the batch operation fails, some
of the keys may have been modified and some may not.

This interface does has the same consistency guarantees as the `store` interface, meaning that
you should be able to "read your writes."

Please note that this interface is bare functions that take a reference to a bucket. This is to
get around the current lack of a way to "extend" a resource with additional methods inside of
wit. Future version of the interface will instead extend these methods on the base `bucket`
resource.
"""
from typing import TypeVar, Generic, Union, Optional, Protocol, Tuple, List, Any, Self
from types import TracebackType
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some
from ..imports import wasi_keyvalue_store


def get_many(bucket: wasi_keyvalue_store.Bucket, keys: List[str]) -> List[Tuple[str, Optional[bytes]]]:
    """
    Get the key-value pairs associated with the keys in the store. It returns a list of
    key-value pairs.
    
    If any of the keys do not exist in the store, it returns a `none` value for that pair in the
    list.
    
    MAY show an out-of-date value if there are concurrent writes to the store.
    
    If any other error occurs, it returns an `Err(error)`.
    
    Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.wasi_keyvalue_store.Error)`
    """
    raise NotImplementedError

def set_many(bucket: wasi_keyvalue_store.Bucket, key_values: List[Tuple[str, bytes]]) -> None:
    """
    Set the values associated with the keys in the store. If the key already exists in the
    store, it overwrites the value.
    
    Note that the key-value pairs are not guaranteed to be set in the order they are provided.
    
    If any of the keys do not exist in the store, it creates a new key-value pair.
    
    If any other error occurs, it returns an `Err(error)`. When an error occurs, it does not
    rollback the key-value pairs that were already set. Thus, this batch operation does not
    guarantee atomicity, implying that some key-value pairs could be set while others might
    fail.
    
    Other concurrent operations may also be able to see the partial results.
    
    Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.wasi_keyvalue_store.Error)`
    """
    raise NotImplementedError

def delete_many(bucket: wasi_keyvalue_store.Bucket, keys: List[str]) -> None:
    """
    Delete the key-value pairs associated with the keys in the store.
    
    Note that the key-value pairs are not guaranteed to be deleted in the order they are
    provided.
    
    If any of the keys do not exist in the store, it skips the key.
    
    If any other error occurs, it returns an `Err(error)`. When an error occurs, it does not
    rollback the key-value pairs that were already deleted. Thus, this batch operation does not
    guarantee atomicity, implying that some key-value pairs could be deleted while others might
    fail.
    
    Other concurrent operations may also be able to see the partial results.
    
    Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.wasi_keyvalue_store.Error)`
    """
    raise NotImplementedError

