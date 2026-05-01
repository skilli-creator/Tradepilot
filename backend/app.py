from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.services.deriv_api import DerivAPI
from backend.bot_state import BotState

app = Flask(__name__)
CORS(app)

bot_state = BotState()
deriv = None   # global API instance


# =========================
# CONNECT DERIV ACCOUNT
# =========================
@app.route("/api/connect", methods=["POST"])
def connect():
    global deriv

    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({"error": "No token provided"}), 400

    deriv = DerivAPI(token)
    deriv.connect()

    return jsonify({"status": "connected", "message": "Deriv connected successfully"})


# =========================
# START BOT
# =========================
@app.route("/api/start-bot", methods=["POST"])
def start_bot():

    if deriv is None:
        return jsonify({"error": "Not connected to Deriv"}), 400

    bot_state.running = True
    bot_state.start_time()

    return jsonify({"status": "bot started"})


# =========================
# STOP BOT
# =========================
@app.route("/api/stop-bot", methods=["POST"])
def stop_bot():

    bot_state.running = False

    return jsonify({"status": "bot stopped"})


# =========================
# GET BOT STATUS
# =========================
@app.route("/api/status", methods=["GET"])
def status():

    return jsonify({
        "running": bot_state.running,
        "profit": bot_state.profit,
        "trades": bot_state.trades
    })


if __name__ == "__main__":
    app.run(debug=True)