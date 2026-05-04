import websocket
import json
import threading
import time

DERIV_WS = "wss://ws.derivws.com/websockets/v3"

class DerivClient:
    def __init__(self, token):
        self.token = token
        self.ws = None
        self.last_response = None
        self.connected = False

    # =========================
    # CONNECT TO DERIV
    # =========================
    def connect(self):
        self.ws = websocket.WebSocketApp(
            DERIV_WS,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        thread.start()

        # wait until connection is ready
        time.sleep(2)

    # =========================
    # AUTHENTICATE
    # =========================
    def on_open(self, ws):
        print("Connected to Deriv WebSocket")

        self.connected = True

        auth_request = {
            "authorize": self.token
        }

        ws.send(json.dumps(auth_request))

    # =========================
    # HANDLE RESPONSE
    # =========================
    def on_message(self, ws, message):
        try:
            self.last_response = json.loads(message)
            print("DERIV RESPONSE:", self.last_response)

        except Exception as e:
            print("Parse error:", e)

    # =========================
    # ERROR HANDLER
    # =========================
    def on_error(self, ws, error):
        print("WebSocket error:", error)

    # =========================
    # CLOSE HANDLER
    # =========================
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")
        self.connected = False

    # =========================
    # SEND REQUEST
    # =========================
    def send(self, payload):
        if not self.ws:
            return {"error": {"message": "WebSocket not connected"}}

        try:
            self.ws.send(json.dumps(payload))

            # wait for response (simple sync method)
            time.sleep(1)

            return self.last_response

        except Exception as e:
            return {"error": {"message": str(e)}}

    # =========================
    # RECEIVE LAST RESPONSE
    # =========================
    def receive(self):
        return self.last_response