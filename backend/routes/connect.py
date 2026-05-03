from flask import Blueprint, request, jsonify
import websocket
import json

connect_bp = Blueprint("connect", __name__)


def verify_deriv_token(token):
    try:
        ws = websocket.create_connection("wss://ws.derivws.com/websockets/v3?app_id=1089")

        # Send authorize request
        ws.send(json.dumps({
            "authorize": token
        }))

        response = json.loads(ws.recv())
        ws.close()

        if "error" in response:
            return False, response["error"]["message"]

        return True, response

    except Exception as e:
        return False, str(e)


@connect_bp.route("/api/connect", methods=["POST"])
def connect_account():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({
            "status": "error",
            "message": "Token missing"
        }), 400

    # 🔥 REAL VALIDATION
    is_valid, result = verify_deriv_token(token)

    if not is_valid:
        return jsonify({
            "status": "error",
            "message": result
        }), 401

    auth = result.get("authorize", {})
    print("DERIV RESPONSE:", result)

    return jsonify({
    "status": "success",
    "message": "Connected successfully",
    "user": {
        "account_id": auth.get("loginid"),
        "balance": auth.get("balance"),
        "currency": auth.get("currency"),
        "email": auth.get("email"),
        "account_type": "Demo" if auth.get("is_virtual") == 1 else "Real"
        
    }
})