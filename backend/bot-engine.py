import time

from backend.state.bot_state import BotState
from backend.services.strategy_engine import generate_signal
from backend.services.risk_manager import check_risk
from backend.services.martingale import next_stake

# NEW: Deriv API connection (IMPORTANT)
from backend.services.deriv_api import DerivAPI

deriv = None


def start_bot(config):

    global deriv

    BotState.running = True

    base_stake = float(config.get("stake", 10))
    tp = float(config.get("tp", 20))
    sl = float(config.get("sl", 10))
    loops = int(config.get("loops", 5))
    martingale = config.get("martingale", "off") == "on"
    trade_type = config.get("tradeType")
    market = config.get("market")

    # NEW: Deriv token from frontend
    token = config.get("token")

    # =========================
    # CONNECT TO DERIV
    # =========================
    deriv = DerivAPI(token)
    deriv.connect()

    BotState.current_stake = base_stake

    # symbol mapping
    symbol_map = {
        "Volatility 100": "R_100",
        "Boom 500": "BOOM500",
        "Crash 1000": "CRASH1000"
    }

    symbol = symbol_map.get(market, "R_100")

    for i in range(loops):

        if not BotState.running:
            break

        # =========================
        # 1. STRATEGY ENGINE
        # =========================
        signal_data = generate_signal(trade_type)

        BotState.confidence = signal_data["confidence"]
        BotState.reasoning = signal_data["reasoning"]

        stake = BotState.current_stake

        # =========================
        # 2. DETERMINE CONTRACT TYPE
        # =========================
        contract_type = "CALL" if signal_data["confidence"] < 75 else "PUT"

        # =========================
        # 3. PLACE REAL TRADE (DERIV)
        # =========================
        deriv.buy_contract(symbol, stake, contract_type)

        # =========================
        # 4. WAIT FOR RESULT (REAL MARKET)
        # NOTE: result updates via websocket in deriv_api.py
        # =========================
        time.sleep(2)

        # =========================
        # 5. UPDATE STAKE (MARTINGALE SAFE)
        # =========================
        if BotState.trades > 0:

            last_trade_win = BotState.profit > 0  # simple indicator

            if last_trade_win:
                BotState.wins += 1
                BotState.current_stake = base_stake
            else:
                BotState.losses += 1
                BotState.current_stake = next_stake(
                    BotState.current_stake,
                    base_stake,
                    martingale
                )

        # =========================
        # 6. RISK CHECK (TP / SL)
        # =========================
        status = check_risk(BotState.profit, tp, sl)

        if status in ["TP_HIT", "SL_HIT"]:
            BotState.running = False
            break

        BotState.trades += 1

        time.sleep(1.5)


def stop_bot():
    BotState.running = False