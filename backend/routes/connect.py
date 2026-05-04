from flask import Blueprint, request, jsonify
import websocket
import json
from backend.database.db import get_db_connection

connect_bp = Blueprint("connect", __name__)


# =========================
# 🔌 VERIFY DERIV TOKEN
# =========================
def verify_deriv_token(token):
    try:
        ws = websocket.create_connection(
            "wss://ws.derivws.com/websockets/v3?app_id=1089"
        )

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


# =========================
# 🚀 CONNECT ACCOUNT
# =========================
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

    # =========================
    # 💰 FIX BALANCE
    # =========================
    balance_raw = float(auth.get("balance", 0))
    balance = balance_raw / 100 if balance_raw > 1000 else balance_raw

    # =========================
    # 📦 EXTRACT USER DATA
    # =========================
    account_id = auth.get("loginid")
    email = auth.get("email")
    currency = auth.get("currency")
    account_type = "Demo" if auth.get("is_virtual") == 1 else "Real"

    # =========================
    # 🔐 SAVE TO DATABASE
    # =========================
    try:
        conn = get_db_connection()

        if conn:
            cursor = conn.cursor()

            print("Checking if user exists...")

            # Check if user exists
            cursor.execute("SELECT * FROM derivdash WHERE account_id = %s", (account_id,))
            existing_user = cursor.fetchone()

            if existing_user:
                print("User exists — updating...")

                cursor.execute("""
                    UPDATE derivdash
                    SET email=%s, token=%s, balance=%s, currency=%s, account_type=%s
                    WHERE account_id=%s
                """, (email, token, balance, currency, account_type, account_id))

            else:
                print("New user — inserting...")

                cursor.execute("""
                    INSERT INTO derivdash (account_id, email, token, balance, currency, account_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (account_id, email, token, balance, currency, account_type))

            conn.commit()
            print("DB operation successful!")

            cursor.close()
            conn.close()

    except Exception as db_error:
        print("DB ERROR:", db_error)

    # =========================
    # ✅ RESPONSE TO FRONTEND
    # =========================
    return jsonify({
        "status": "success",
        "message": "Connected successfully",
        "token": token,
        "user": {
            "account_id": account_id,
            "balance": round(balance, 2),
            "currency": currency,
            "email": email,
            "account_type": account_type
        }
    })