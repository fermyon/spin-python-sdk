from spin_http import Response
import toml

def handle_request(request):

    some_toml = """
    title = "foo"
    [bar]
    baz = "wow"
    such = "toml"
    """

    return Response(200,
                    {"content-type": "text/plain"},
                    bytes(f"Toml content:{toml.loads(some_toml)}", "utf-8"))
