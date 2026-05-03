from flask import Blueprint, request, jsonify
from backend.bot_engine import start_bot, stop_bot
from backend.bot_state import BotState
import threading

bot_bp = Blueprint("bot", __name__)

bot_thread = None


# =========================
# START BOT
# =========================
@bot_bp.route("/start-bot", methods=["POST"])
def start():
    global bot_thread

    try:
        # جلوگیری از اجرای چندباره
        if BotState.running:
            return jsonify({"status": "Bot already running"}), 400

        config = request.json

        bot_thread = threading.Thread(target=start_bot, args=(config,))
        bot_thread.daemon = True
        bot_thread.start()

        return jsonify({"status": "bot started"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# STOP BOT
# =========================
@bot_bp.route("/stop-bot", methods=["POST"])
def stop():
    try:
        stop_bot()
        return jsonify({"status": "bot stopped"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# LIVE STATUS
# =========================
@bot_bp.route("/bot-status", methods=["GET"])
def status():

    try:
        win_rate = 0
        if BotState.trades > 0:
            win_rate = (BotState.wins / BotState.trades) * 100

        return jsonify({
            "running": BotState.running,

            # PERFORMANCE
            "profit": round(BotState.profit, 2),
            "balance": round(getattr(BotState, "balance", 0), 2),

            # STATS
            "wins": BotState.wins,
            "losses": BotState.losses,
            "trades": BotState.trades,
            "win_rate": round(win_rate, 2),

            # STRATEGY
            "confidence": BotState.confidence,
            "reasoning": BotState.reasoning,

            # LIVE BOT DATA
            "current_stake": getattr(BotState, "current_stake", 0),
            "last_result": getattr(BotState, "last_result", None)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500