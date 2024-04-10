"""Module with helpers for wasi http"""

import asyncio
import traceback
from spin_sdk.http import poll_loop
from spin_sdk.http.poll_loop import PollLoop, Sink, Stream
from spin_sdk.wit import exports
from spin_sdk.wit.types import Ok, Err
from spin_sdk.wit.imports.types import (
    IncomingResponse, Method, Method_Get, Method_Head, Method_Post, Method_Put, Method_Delete, Method_Connect, Method_Options,
    Method_Trace, Method_Patch, Method_Other, IncomingRequest, IncomingBody, ResponseOutparam, OutgoingResponse,
    Fields, Scheme, Scheme_Http, Scheme_Https, Scheme_Other, OutgoingRequest, OutgoingBody
)
from spin_sdk.wit.imports.streams import StreamError_Closed
from dataclasses import dataclass
from collections.abc import MutableMapping
from typing import Optional
from urllib import parse

@dataclass
class Request:
    """An HTTP request"""
    method: str
    uri: str
    headers: MutableMapping[str, str]
    body: Optional[bytes]

@dataclass
class Response:
    """An HTTP response"""
    status: int
    headers: MutableMapping[str, str]
    body: Optional[bytes]

class IncomingHandler(exports.IncomingHandler):
    """Simplified handler for incoming HTTP requests using blocking, buffered I/O."""
    
    def handle_request(self, request: Request) -> Response:
        """Handle an incoming HTTP request and return a response or raise an error"""
        raise NotImplementedError
    
    def handle(self, request: IncomingRequest, response_out: ResponseOutparam):
        method = request.method()

        if isinstance(method, Method_Get):
            method_str = "GET"
        elif isinstance(method, Method_Head):
            method_str = "HEAD"
        elif isinstance(method, Method_Post):
            method_str = "POST"
        elif isinstance(method, Method_Put):
            method_str = "PUT"
        elif isinstance(method, Method_Delete):
            method_str = "DELETE"
        elif isinstance(method, Method_Connect):
            method_str = "CONNECT"
        elif isinstance(method, Method_Options):
            method_str = "OPTIONS"
        elif isinstance(method, Method_Trace):
            method_str = "TRACE"
        elif isinstance(method, Method_Patch):
            method_str = "PATCH"
        elif isinstance(method, Method_Other):
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
                if isinstance(e.value, StreamError_Closed):
                    request_stream.__exit__()
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
            response.set_status_code(500)
            ResponseOutparam.set(response_out, Ok(response))
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
        response_stream.__exit__()
        OutgoingBody.finish(response_body, None)
    
def send(request: Request) -> Response:
    """Send an HTTP request and return a response or raise an error"""
    loop = PollLoop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(send_async(request))
    

async def send_async(request: Request) -> Response:
    match request.method:
        case "GET":
            method: Method = Method_Get()
        case "HEAD":
            method = Method_Head()
        case "POST":
            method = Method_Post()
        case "PUT":
            method = Method_Put()
        case "DELETE":
            method = Method_Delete()
        case "CONNECT":
            method = Method_Connect()
        case "OPTIONS":
            method = Method_Options()
        case "TRACE":
            method = Method_Trace()
        case "PATCH":
            method = Method_Patch()
        case _:
            method = Method_Other(request.method)
    
    url_parsed = parse.urlparse(request.uri)

    match url_parsed.scheme:
        case "http":
            scheme: Scheme = Scheme_Http()
        case "https":
            scheme = Scheme_Https()
        case _:
            scheme = Scheme_Other(url_parsed.scheme)

    if request.headers.get('content-length') is None:
        content_length = len(request.body) if request.body is not None else 0
        request.headers['content-length'] = str(content_length)

    headers = list(map(
        lambda pair: (pair[0], bytes(pair[1], "utf-8")),
        request.headers.items()
    ))
    print("Header length", request.headers.get('content-length'))

    outgoing_request = OutgoingRequest(Fields.from_list(headers))
    outgoing_request.set_method(method)
    outgoing_request.set_scheme(scheme)
    outgoing_request.set_authority(url_parsed.netloc)
    outgoing_request.set_path_with_query(url_parsed.path)

    outgoing_body = request.body if request.body is not None else bytearray()
    sink = Sink(outgoing_request.body())
    incoming_response: IncomingResponse = (await asyncio.gather(
        poll_loop.send(outgoing_request),
        sink.send(outgoing_body)
    ))[0]

    sink.close()

    response_body = Stream(incoming_response.consume())
    body = bytearray()
    while True:
        chunk = await response_body.next()
        if chunk is None:
            simple_response = Response(
                incoming_response.status(),
                dict(map(
                    lambda pair: (pair[0], str(pair[1], "utf-8")),
                    incoming_response.headers().entries()
                )),
                bytes(body)
            )
            incoming_response.__exit__()
            return simple_response
        else:
            body += chunk

