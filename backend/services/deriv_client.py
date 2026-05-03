import websocket
import json
import threading

DERIV_WS = "wss://ws.derivws.com/websockets/v3"

class DerivClient:
    def __init__(self, token):
        self.token = token
        self.ws = None

    def connect(self):
        self.ws = websocket.WebSocketApp(
            DERIV_WS,
            on_open=self.on_open,
            on_message=self.on_message
        )

        thread = threading.Thread(target=self.ws.run_forever)
        thread.start()

    def on_open(self, ws):
        auth_request = {
            "authorize": self.token
        }
        ws.send(json.dumps(auth_request))

    def on_message(self, ws, message):
        print("DERIV RESPONSE:", message)

    def buy_contract(self, contract):
        self.ws.send(json.dumps(contract))