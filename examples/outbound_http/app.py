from spin_http import Request, Response, http_send


def handle_request(request):

    response = http_send(
        Request("GET", "https://some-random-api.ml/facts/dog", [], None))

    return Response(200,
                    [("content-type", "text/plain")],
                    bytes(f"Here is a dog fact: {str(response.body, 'utf-8')}", "utf-8"))
