from flask import Blueprint, request, jsonify
from threading import Thread
from services.bot_engine import run_bot
import bot_state

bot_bp = Blueprint("bot_bp", __name__)

latest_results = []
@bot_bp.route("/start", methods=["POST"])
def start_bot():
    global latest_results

    if bot_state.bot_running:
        return jsonify({"message": "Bot already running"}), 400

    config = request.json
    latest_results = []
    bot_state.bot_running = True

    def callback(data):
        latest_results.append(data)
        print("TRADE:", data)

    def run():
        run_bot(config, callback)
        bot_state.bot_running = False

    bot_state.bot_thread = Thread(target=run)
    bot_state.bot_thread.start()

    return jsonify({"message": "Bot started"})
@bot_bp.route("/stop", methods=["POST"])
def stop_bot():
    bot_state.bot_running = False
    return jsonify({"message": "Bot stopped"})
@bot_bp.route("/results", methods=["GET"])
def results():
    return jsonify({"data": latest_results})