"""
A keyvalue interface that provides eventually consistent key-value operations.

Each of these operations acts on a single key-value pair.

The value in the key-value pair is defined as a `u8` byte array and the intention is that it is
the common denominator for all data types defined by different key-value stores to handle data,
ensuring compatibility between different key-value stores. Note: the clients will be expecting
serialization/deserialization overhead to be handled by the key-value store. The value could be
a serialized object from JSON, HTML or vendor-specific data types like AWS S3 objects.

Data consistency in a key value store refers to the guarantee that once a write operation
completes, all subsequent read operations will return the value that was written.

Any implementation of this interface must have enough consistency to guarantee "reading your
writes." In particular, this means that the client should never get a value that is older than
the one it wrote, but it MAY get a newer value if one was written around the same time. These
guarantees only apply to the same client (which will likely be provided by the host or an
external capability of some kind). In this context a "client" is referring to the caller or
guest that is consuming this interface. Once a write request is committed by a specific client,
all subsequent read requests by the same client will reflect that write or any subsequent
writes. Another client running in a different context may or may not immediately see the result
due to the replication lag. As an example of all of this, if a value at a given key is A, and
the client writes B, then immediately reads, it should get B. If something else writes C in
quick succession, then the client may get C. However, a client running in a separate context may
still see A or B
"""
from typing import TypeVar, Generic, Union, Optional, Protocol, Tuple, List, Any, Self
from types import TracebackType
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some



@dataclass
class Error_NoSuchStore:
    pass


@dataclass
class Error_AccessDenied:
    pass


@dataclass
class Error_Other:
    value: str


Error = Union[Error_NoSuchStore, Error_AccessDenied, Error_Other]
"""
The set of errors which may be raised by functions in this package
"""


@dataclass
class KeyResponse:
    """
    A response to a `list-keys` operation.
    """
    keys: List[str]
    cursor: Optional[str]

class Bucket:
    """
    A bucket is a collection of key-value pairs. Each key-value pair is stored as a entry in the
    bucket, and the bucket itself acts as a collection of all these entries.
    
    It is worth noting that the exact terminology for bucket in key-value stores can very
    depending on the specific implementation. For example:
    
    1. Amazon DynamoDB calls a collection of key-value pairs a table
    2. Redis has hashes, sets, and sorted sets as different types of collections
    3. Cassandra calls a collection of key-value pairs a column family
    4. MongoDB calls a collection of key-value pairs a collection
    5. Riak calls a collection of key-value pairs a bucket
    6. Memcached calls a collection of key-value pairs a slab
    7. Azure Cosmos DB calls a collection of key-value pairs a container
    
    In this interface, we use the term `bucket` to refer to a collection of key-value pairs
    """
    
    def get(self, key: str) -> Optional[bytes]:
        """
        Get the value associated with the specified `key`
        
        The value is returned as an option. If the key-value pair exists in the
        store, it returns `Ok(value)`. If the key does not exist in the
        store, it returns `Ok(none)`.
        
        If any other error occurs, it returns an `Err(error)`.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.wasi_keyvalue_store.Error)`
        """
        raise NotImplementedError
    def set(self, key: str, value: bytes) -> None:
        """
        Set the value associated with the key in the store. If the key already
        exists in the store, it overwrites the value.
        
        If the key does not exist in the store, it creates a new key-value pair.
        
        If any other error occurs, it returns an `Err(error)`.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.wasi_keyvalue_store.Error)`
        """
        raise NotImplementedError
    def delete(self, key: str) -> None:
        """
        Delete the key-value pair associated with the key in the store.
        
        If the key does not exist in the store, it does nothing.
        
        If any other error occurs, it returns an `Err(error)`.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.wasi_keyvalue_store.Error)`
        """
        raise NotImplementedError
    def exists(self, key: str) -> bool:
        """
        Check if the key exists in the store.
        
        If the key exists in the store, it returns `Ok(true)`. If the key does
        not exist in the store, it returns `Ok(false)`.
        
        If any other error occurs, it returns an `Err(error)`.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.wasi_keyvalue_store.Error)`
        """
        raise NotImplementedError
    def list_keys(self, cursor: Optional[str]) -> KeyResponse:
        """
        Get all the keys in the store with an optional cursor (for use in pagination). It
        returns a list of keys. Please note that for most KeyValue implementations, this is a
        can be a very expensive operation and so it should be used judiciously. Implementations
        can return any number of keys in a single response, but they should never attempt to
        send more data than is reasonable (i.e. on a small edge device, this may only be a few
        KB, while on a large machine this could be several MB). Any response should also return
        a cursor that can be used to fetch the next page of keys. See the `key-response` record
        for more information.
        
        Note that the keys are not guaranteed to be returned in any particular order.
        
        If the store is empty, it returns an empty list.
        
        MAY show an out-of-date list of keys if there are concurrent writes to the store.
        
        If any error occurs, it returns an `Err(error)`.
        
        Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.wasi_keyvalue_store.Error)`
        """
        raise NotImplementedError
    def __enter__(self) -> Self:
        """Returns self"""
        return self
                                
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> bool | None:
        """
        Release this resource.
        """
        raise NotImplementedError



def open(identifier: str) -> Bucket:
    """
    Get the bucket with the specified identifier.
    
    `identifier` must refer to a bucket provided by the host.
    
    `error::no-such-store` will be raised if the `identifier` is not recognized.
    
    Raises: `spin_sdk.wit.types.Err(spin_sdk.wit.imports.wasi_keyvalue_store.Error)`
    """
    raise NotImplementedError

