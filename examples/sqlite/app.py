from spin_http import Response
from spin_sqlite import sqlite_open_default

def handle_request(request):
    conn = sqlite_open_default();
    result = conn.execute("SELECT * FROM todos WHERE id > (?);", [1])
    return Response(200,
                    {"content-type": "application/json"},
                    bytes(str(result.rows()), "utf-8"))
