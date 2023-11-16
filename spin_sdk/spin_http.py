"""Module for sending outbound HTTP requests"""

from dataclasses import dataclass
from collections.abc import Mapping
from typing import Optional

@dataclass
class Request:
    """An HTTP request"""
    method: str
    uri: str
    headers: Mapping[str, str]
    body: Optional[bytes]

@dataclass
class Response:
    """An HTTP response"""
    status: int
    headers: Mapping[str, str]
    body: Optional[bytes]

def http_send(request: Request) -> Response:
    """Send an HTTP request and return a response or raise an error"""
    raise NotImplementedError
