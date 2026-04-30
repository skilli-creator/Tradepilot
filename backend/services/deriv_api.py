import websocket
import json
import threading
import time

from backend.state.bot_state import BotState

DERIV_APP_ID = "1089"
DERIV_WS_URL = f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"

class DerivAPI:

    def __init__(self, token):
        self.token = token
        self.ws = None
        self.authenticated = False

    # =========================
    # CONNECT
    # =========================
    def connect(self):
        self.ws = websocket.WebSocketApp(
            DERIV_WS_URL,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        thread = threading.Thread(target=self.ws.run_forever)
        thread.start()

    # =========================
    # OPEN CONNECTION
    # =========================
    def on_open(self, ws):
        print("Connected to Deriv API")

        auth_data = {
            "authorize": self.token
        }

        ws.send(json.dumps(auth_data))

    # =========================
    # MESSAGE HANDLER
    # =========================
    def on_message(self, ws, message):
        data = json.loads(message)

        # AUTH SUCCESS
        if data.get("msg_type") == "authorize":
            self.authenticated = True
            print("AUTH SUCCESS ✔")

        # TRADE RESULT
        if data.get("msg_type") == "buy":
            print("TRADE EXECUTED:", data)

        if data.get("msg_type") == "proposal_open_contract":
            contract = data["proposal_open_contract"]

            # WIN/LOSS UPDATE
            if contract["status"] == "sold":
                profit = float(contract["profit"])

                BotState.profit += profit
                BotState.trades += 1

                if profit > 0:
                    BotState.wins += 1
                else:
                    BotState.losses += 1

    # =========================
    # ERROR
    # =========================
    def on_error(self, ws, error):
        print("ERROR:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection closed")

    # =========================
    # PLACE TRADE
    # =========================
    def buy_contract(self, symbol, stake, contract_type):

        if not self.authenticated:
            print("Not authenticated yet")
            return

        proposal = {
            "proposal": 1,
            "amount": stake,
            "basis": "stake",
            "contract_type": contract_type,  # CALL or PUT
            "currency": "USD",
            "duration": 5,
            "duration_unit": "m",
            "symbol": symbol
        }

        self.ws.send(json.dumps(proposal))