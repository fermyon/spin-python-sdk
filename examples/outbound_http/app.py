from spin_http import Request, Response, http_send


def handle_request(request):

    response = http_send(
        Request("GET", "https://random-data-api.fermyon.app/physics/json", {}, None))

    return Response(200,
                    {"content-type": "text/plain"},
                    bytes(f"Here is a physics fact: {str(response.body, 'utf-8')}", "utf-8"))
