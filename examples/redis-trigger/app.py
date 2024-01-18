from spin_sdk.wit import exports

class InboundRedis(exports.InboundRedis):
    def handle_message(self, message: bytes):
        print(message)