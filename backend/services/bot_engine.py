import time

from backend.bot_state import BotState
from backend.strategy_engine import generate_signal
from backend.risk_manager import check_risk
from backend.martingale import next_stake

from backend.services.deriv_api import DerivAPI

deriv = None


def start_bot(config):
    global deriv

    BotState.running = True

    base_stake = float(config.get("stake", 10))
    tp = float(config.get("tp", 20))
    sl = float(config.get("sl", 10))
    loops = int(config.get("loops", 5))
    martingale_enabled = config.get("martingale", "off") == "on"
    trade_type = config.get("tradeType")
    market = config.get("market")
    token = config.get("token")

    # =========================
    # CONNECT TO DERIV
    # =========================
    deriv = DerivAPI(token)
    deriv.connect()

    # ⏳ WAIT FOR AUTH (IMPORTANT)
    while not deriv.authenticated:
        print("Waiting for Deriv auth...")
        time.sleep(1)

    BotState.current_stake = base_stake
    BotState.last_result = None

    # SYMBOL MAP
    symbol_map = {
        "Volatility 100": "R_100",
        "Boom 500": "BOOM500",
        "Crash 1000": "CRASH1000"
    }

    symbol = symbol_map.get(market, "R_100")

    loop_count = 0

    while BotState.running and loop_count < loops:

        # =========================
        # 🚫 WAIT IF TRADE STILL RUNNING
        # =========================
        if deriv.current_contract_id is not None:
            time.sleep(1)
            continue

        print("Starting new trade...")

        # =========================
        # 1. STRATEGY
        # =========================
        signal_data = generate_signal(trade_type)

        BotState.confidence = signal_data["confidence"]
        BotState.reasoning = signal_data["reasoning"]

        stake = BotState.current_stake

        # =========================
        # 2. CONTRACT TYPE
        # =========================
        contract_type = "CALL" if signal_data["confidence"] < 75 else "PUT"

        # =========================
        # 3. PLACE TRADE
        # =========================
        deriv.buy_contract(symbol, stake, contract_type)

        # =========================
        # 4. WAIT FOR RESULT (REAL)
        # =========================
        prev_trades = BotState.trades

        while BotState.trades == prev_trades:
            time.sleep(1)

        print("Trade finished:", BotState.last_result)

        # =========================
        # 5. MARTINGALE LOGIC
        # =========================
        if BotState.last_result == "win":
            BotState.current_stake = base_stake
        else:
            BotState.current_stake = next_stake(
                BotState.current_stake,
                base_stake,
                martingale_enabled
            )

        # =========================
        # 6. RISK MANAGEMENT
        # =========================
        status = check_risk(BotState.profit, tp, sl)

        if status in ["TP_HIT", "SL_HIT"]:
            print("Risk limit reached:", status)
            BotState.running = False
            break

        loop_count += 1

        time.sleep(1)

    print("Bot stopped")


def stop_bot():
    BotState.running = False