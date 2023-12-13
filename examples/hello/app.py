from spin_http import exports
from spin_http.types import Ok
from spin_http.imports import types, variables
from spin_http.imports.types import (
    MethodGet, MethodPost, Scheme, SchemeHttp, SchemeHttps, SchemeOther, IncomingRequest, ResponseOutparam,
    OutgoingResponse, Fields, OutgoingBody, OutgoingRequest
)

class IncomingHandler(exports.IncomingHandler):
    def handle(self, request: IncomingRequest, response_out: ResponseOutparam):
        method = request.method()

        if isinstance(method, MethodGet):
            response = OutgoingResponse(Fields.from_list([("content-type", b"text/plain")]))
            body = response.body()
            ResponseOutparam.set(response_out, Ok(response))
            stream = body.write()
            stream.blocking_write_and_flush(bytes(variables.get("message"), "utf-8"))
            stream.drop()
            OutgoingBody.finish(body, None)
        else:
            response = OutgoingResponse(Fields())
            body = response.body()
            response.set_status_code(400)
            ResponseOutparam.set(response_out, Ok(response))
            OutgoingBody.finish(body, None)
