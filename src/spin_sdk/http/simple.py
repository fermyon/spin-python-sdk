import traceback

from spin_sdk.wit import exports
from spin_sdk.wit.types import Ok, Err
from spin_sdk.wit.imports import types, outgoing_handler
from spin_sdk.wit.imports.types import (
    Method, MethodGet, MethodHead, MethodPost, MethodPut, MethodDelete, MethodConnect, MethodOptions, MethodTrace,
    MethodPatch, MethodOther, IncomingRequest, IncomingBody, ResponseOutparam, OutgoingResponse, Fields, Scheme,
    SchemeHttp, SchemeHttps, SchemeOther, OutgoingRequest, OutgoingBody
)
from spin_sdk.wit.imports.streams import StreamErrorClosed
from dataclasses import dataclass
from collections.abc import Mapping
from typing import Optional
from urllib import parse

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

class IncomingHandler(exports.IncomingHandler):
    """Simplified handler for incoming HTTP requests using blocking, buffered I/O."""
    
    def handle_request(self, request: Request) -> Response:
        """Handle an incoming HTTP request and return a response or raise an error"""
        raise NotImplementedError
    
    def handle(self, request: IncomingRequest, response_out: ResponseOutparam):
        method = request.method()

        if isinstance(method, MethodGet):
            method_str = "GET"
        elif isinstance(method, MethodHead):
            method_str = "HEAD"
        elif isinstance(method, MethodPost):
            method_str = "POST"
        elif isinstance(method, MethodPut):
            method_str = "PUT"
        elif isinstance(method, MethodDelete):
            method_str = "DELETE"
        elif isinstance(method, MethodConnect):
            method_str = "CONNECT"
        elif isinstance(method, MethodOptions):
            method_str = "OPTIONS"
        elif isinstance(method, MethodTrace):
            method_str = "TRACE"
        elif isinstance(method, MethodPatch):
            method_str = "PATCH"
        elif isinstance(method, MethodOther):
            method_str = method.value
        else:
            raise AssertionError

        request_body = request.consume()
        request_stream = request_body.stream()
        body = bytearray()
        while True:
            try:
                body += request_stream.blocking_read(16 * 1024)
            except Err as e:
                if isinstance(e.value, StreamErrorClosed):
                    request_stream.drop()
                    IncomingBody.finish(request_body)
                    break
                else:
                    raise e

        request_uri = request.path_with_query()
        if request_uri is None:
            uri = "/"
        else:
            uri = request_uri

        try:
            simple_response = self.handle_request(Request(
                method_str,
                uri,
                dict(map(lambda pair: (pair[0], str(pair[1], "utf-8")), request.headers().entries())),
                bytes(body)
            ))
        except:
            traceback.print_exc()

            response = OutgoingResponse(Fields())
            response_body = response.body()
            response.set_status_code(500)
            ResponseOutparam.set(response_out, Ok(response))
            OutgoingBody.finish(response_body, None)
            return

        response = OutgoingResponse(Fields.from_list(list(map(
            lambda pair: (pair[0], bytes(pair[1], "utf-8")),
            simple_response.headers.items()
        ))))
        response_body = response.body()
        response.set_status_code(simple_response.status)
        ResponseOutparam.set(response_out, Ok(response))
        response_stream = response_body.write()
        if simple_response.body is not None:
            MAX_BLOCKING_WRITE_SIZE = 4096
            offset = 0
            while offset < len(simple_response.body):
                count = min(len(simple_response.body) - offset, MAX_BLOCKING_WRITE_SIZE)
                response_stream.blocking_write_and_flush(simple_response.body[offset:offset+count])
                offset += count
        response_stream.drop()
        OutgoingBody.finish(response_body, None)
    
def send(request: Request) -> Response:
    """Send an HTTP request and return a response or raise an error"""

    match request.method:
        case "GET":
            method: Method = MethodGet()
        case "HEAD":
            method = MethodHead()
        case "POST":
            method = MethodPost()
        case "PUT":
            method = MethodPut()
        case "DELETE":
            method = MethodDelete()
        case "CONNECT":
            method = MethodConnect()
        case "OPTIONS":
            method = MethodOptions()
        case "TRACE":
            method = MethodTrace()
        case "PATCH":
            method = MethodPatch()
        case _:
            method = MethodOther(request.method)
    
    url_parsed = parse.urlparse(request.uri)

    match url_parsed.scheme:
        case "http":
            scheme: Scheme = SchemeHttp()
        case "https":
            scheme = SchemeHttps()
        case _:
            scheme = SchemeOther(url_parsed.scheme)

    outgoing_request = OutgoingRequest(Fields.from_list(list(map(
        lambda pair: (pair[0], bytes(pair[1], "utf-8")),
        request.headers.items()
    ))))
    outgoing_request.set_method(method)
    outgoing_request.set_scheme(scheme)
    outgoing_request.set_authority(url_parsed.netloc)
    outgoing_request.set_path_with_query(url_parsed.path)

    if request.body is not None:
        raise NotImplementedError("todo: handle outgoing request bodies")

    future = outgoing_handler.handle(outgoing_request, None)
    pollable = future.subscribe()

    while True:
        response = future.get()
        if response is None:
            pollable.block()
        else:
            pollable.drop()
            future.drop()
            
            if isinstance(response, Ok):
                if isinstance(response.value, Ok):
                    response_value = response.value.value
                    response_body = response_value.consume()
                    response_stream = response_body.stream()
                    body = bytearray()
                    while True:
                        try:
                            body += response_stream.blocking_read(16 * 1024)
                        except Err as e:
                            if isinstance(e.value, StreamErrorClosed):
                                response_stream.drop()
                                IncomingBody.finish(response_body)
                                simple_response = Response(
                                    response_value.status(),
                                    dict(map(
                                        lambda pair: (pair[0], str(pair[1], "utf-8")),
                                        response_value.headers().entries()
                                    )),
                                    bytes(body)
                                )
                                response_value.drop()
                                return simple_response
                            else:
                                raise e
                else:
                    raise response.value
            else:
                raise response
