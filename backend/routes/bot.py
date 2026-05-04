from flask import Blueprint, request, jsonify
import threading
import time
import random
import websocket
import json

bot_bp = Blueprint("bot", __name__)

# 🔥 GLOBAL BOT STATE (shared with frontend)
bot_state = {
    "running": False,
    "profit": 0,
    "trades": 0,
    "history": []
}


def run_bot(data):

    global bot_state

    token = data.get("token")
    market = data.get("market", "R_100")
    loops = int(data.get("loops", 5))
    tp = float(data.get("tp", 50))
    sl = float(data.get("sl", 20))
    martingale = data.get("martingale") == "on"

    stake = 0.35
    current_stake = stake

    bot_state["running"] = True
    bot_state["profit"] = 0
    bot_state["trades"] = 0
    bot_state["history"] = []

    try:
        ws = websocket.create_connection(
            "wss://ws.derivws.com/websockets/v3?app_id=1089"
        )

        # 🔐 AUTHORIZE
        ws.send(json.dumps({"authorize": token}))
        ws.recv()

        for i in range(loops):

            if not bot_state["running"]:
                break

            # 🎯 RANDOM OVER/UNDER
            contract_type = random.choice(["DIGITOVER", "DIGITUNDER"])
            barrier = random.randint(0, 9)

            # 📊 PROPOSAL
            ws.send(json.dumps({
                "proposal": 1,
                "amount": current_stake,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": 1,
                "duration_unit": "t",
                "symbol": market,
                "barrier": str(barrier)
            }))

            proposal = json.loads(ws.recv())

            if "error" in proposal:
                continue

            proposal_id = proposal["proposal"]["id"]

            # 💰 BUY
            ws.send(json.dumps({
                "buy": proposal_id,
                "price": current_stake
            }))

            buy = json.loads(ws.recv())

            if "error" in buy:
                continue

            contract_id = buy["buy"]["contract_id"]

            # ⏳ WAIT RESULT
            time.sleep(2)

            # 📡 CHECK RESULT
            ws.send(json.dumps({
                "proposal_open_contract": 1,
                "contract_id": contract_id
            }))

            result = json.loads(ws.recv())

            pnl = result["proposal_open_contract"].get("profit", 0)

            # 📊 UPDATE STATE
            bot_state["profit"] += pnl
            bot_state["trades"] += 1

            bot_state["history"].append({
                "stake": current_stake,
                "type": contract_type,
                "result": pnl
            })

            # 🎯 MARTINGALE
            if pnl < 0 and martingale:
                current_stake *= 2
            else:
                current_stake = stake

            # 🛑 STOP CONDITIONS
            if bot_state["profit"] >= tp or bot_state["profit"] <= -sl:
                break

            time.sleep(1)

        ws.close()

    except Exception as e:
        print("BOT ERROR:", e)

    bot_state["running"] = False


@bot_bp.route("/start", methods=["POST"])
def start_bot():
    data = request.get_json()

    if not data.get("token"):
        return jsonify({"error": "Token required"}), 400

    thread = threading.Thread(target=run_bot, args=(data,))
    thread.start()

    return jsonify({"status": "Bot started"})


@bot_bp.route("/status", methods=["GET"])
def get_status():
    return jsonify(bot_state)


@bot_bp.route("/stop", methods=["POST"])
def stop_bot():
    bot_state["running"] = False
    return jsonify({"status": "Bot stopped"})