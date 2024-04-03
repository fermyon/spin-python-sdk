from spin_sdk import http, mqtt 
from spin_sdk.mqtt import Qos
from spin_sdk.http import Request, Response

class IncomingHandler(http.IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        with mqtt.open("mqtt://localhost:1883?client_id=client001", "user", "password", 30) as conn:
            conn.publish("telemetry", bytes("Eureka!", "utf-8"), Qos.AT_LEAST_ONCE)

        return Response(
            200,
            {"content-type": "text/plain"},
            bytes("Sent outbound mqtt message!", "utf-8")
        )
