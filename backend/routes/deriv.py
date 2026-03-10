from flask import Blueprint, jsonify, request
import requests

deriv_bp = Blueprint("deriv", __name__)

DERIV_API_URL = "https://api.deriv.com"  # base URL placeholder

# Balance endpoint
@deriv_bp.route("/balance", methods=["GET"])
def get_balance():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Token required"}), 400

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{DERIV_API_URL}/balance", headers=headers)

    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"error": "Failed to fetch balance"}), response.status_code


# Trade execution endpoint
@deriv_bp.route("/trade", methods=["POST"])
def execute_trade():
    data = request.json
    token = data.get("token")
    market = data.get("market")
    stake = data.get("stake")

    if not token or not market or not stake:
        return jsonify({"error": "Missing required fields"}), 400

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"market": market, "stake": stake}

    response = requests.post(f"{DERIV_API_URL}/trade", headers=headers, json=payload)

    return jsonify(response.json()), response.status_code
