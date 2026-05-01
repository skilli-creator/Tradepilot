from flask import Blueprint, request, jsonify
from backend.bot_engine import start_bot, stop_bot
from backend.bot_state import BotState
import threading

bot_bp = Blueprint("bot", __name__)

# START BOT
@bot_bp.route("/start-bot", methods=["POST"])
def start():

    config = request.json

    thread = threading.Thread(target=start_bot, args=(config,))
    thread.start()

    return jsonify({"status": "bot started"})


# STOP BOT
@bot_bp.route("/stop-bot", methods=["POST"])
def stop():

    stop_bot()

    return jsonify({"status": "bot stopped"})


# LIVE STATUS
@bot_bp.route("/bot-status", methods=["GET"])
def status():

    win_rate = 0
    if BotState.trades > 0:
        win_rate = (BotState.wins / BotState.trades) * 100

    return jsonify({
        "running": BotState.running,
        "profit": round(BotState.profit, 2),
        "wins": BotState.wins,
        "losses": BotState.losses,
        "win_rate": round(win_rate, 2),
        "confidence": BotState.confidence,
        "reasoning": BotState.reasoning
    })