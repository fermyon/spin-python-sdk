"""Module for utilizing Spin Outbound MQTT"""

from enum import Enum
from spin_sdk.wit.imports.mqtt import Connection, Qos as Qos 

def open(address: str, username: str, password: str, keep_alive_interval_in_secs: int) -> Connection:
    """
    Open a connection to the Mqtt instance at `address`.
    
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.mqtt.Error_InvalidAddress)` will be raised if the connection string is invalid.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.mqtt.Error_TooManyConnections)` will be raised if there are too many open connections. Closing one or more previously opened connection using the `__exit__` method might help.
    
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.mqtt.Error_ConnectionFailed)` will be raised if the connection failed.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.mqtt.Error_Other(str))` when some other error occurs.
    """
    return Connection.open(address, username, password, keep_alive_interval_in_secs)
