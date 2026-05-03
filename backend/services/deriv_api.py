import websocket
import json
import threading
import time

from backend.bot_state import BotState

DERIV_APP_ID = "1089"
DERIV_WS_URL = f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"


class DerivAPI:

    def __init__(self, token):
        self.token = token
        self.ws = None
        self.authenticated = False
        self.current_proposal_id = None
        self.current_contract_id = None
        self.connected = False

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
        thread.daemon = True
        thread.start()

    # =========================
    # OPEN CONNECTION
    # =========================
    def on_open(self, ws):
        print("Connected to Deriv API")
        self.connected = True

        ws.send(json.dumps({
            "authorize": self.token
        }))

    # =========================
    # MESSAGE HANDLER
    # =========================
    def on_message(self, ws, message):
        data = json.loads(message)

        msg_type = data.get("msg_type")

        # ================= AUTH
        if msg_type == "authorize":
            self.authenticated = True
            print("AUTH SUCCESS ✔")

            # Get balance immediately
            self.get_balance()

        # ================= BALANCE
        elif msg_type == "balance":
            balance = data["balance"]["balance"]
            BotState.balance = balance
            print("Balance:", balance)

        # ================= PROPOSAL RECEIVED → BUY
        elif msg_type == "proposal":
            proposal_id = data["proposal"]["id"]
            self.current_proposal_id = proposal_id

            buy_req = {
                "buy": proposal_id,
                "price": BotState.stake
            }

            ws.send(json.dumps(buy_req))

        # ================= BUY RESPONSE
        elif msg_type == "buy":
            contract_id = data["buy"]["contract_id"]
            self.current_contract_id = contract_id

            print("TRADE PLACED ✔", contract_id)

            # Subscribe to contract updates
            ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id,
                "subscribe": 1
            }))

        # ================= CONTRACT RESULT
        elif msg_type == "proposal_open_contract":
            contract = data["proposal_open_contract"]

            if contract["is_sold"]:
                profit = float(contract["profit"])

                BotState.trades += 1
                BotState.profit += profit

                if profit > 0:
                    BotState.wins += 1
                    BotState.last_result = "win"
                else:
                    BotState.losses += 1
                    BotState.last_result = "loss"

                print("RESULT:", BotState.last_result, "| Profit:", profit)

                # Reset contract
                self.current_contract_id = None

                # Refresh balance after trade
                self.get_balance()

        # ================= ERROR
        elif "error" in data:
            print("DERIV ERROR:", data["error"])

    # =========================
    # ERROR
    # =========================
    def on_error(self, ws, error):
        print("ERROR:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection closed")
        self.connected = False
        self.authenticated = False

        # 🔁 AUTO RECONNECT
        time.sleep(3)
        print("Reconnecting...")
        self.connect()

    # =========================
    # GET BALANCE
    # =========================
    def get_balance(self):
        if self.authenticated:
            self.ws.send(json.dumps({
                "balance": 1,
                "subscribe": 1
            }))

    # =========================
    # PLACE TRADE
    # =========================
    def buy_contract(self, symbol, stake, contract_type):

        if not self.authenticated:
            print("Not authenticated yet")
            return

        if self.current_contract_id:
            print("Trade already running...")
            return

        BotState.stake = stake  # sync stake

        proposal = {
            "proposal": 1,
            "amount": stake,
            "basis": "stake",
            "contract_type": contract_type,  # CALL / PUT
            "currency": "USD",
            "duration": 1,
            "duration_unit": "m",
            "symbol": symbol
        }

        self.ws.send(json.dumps(proposal))