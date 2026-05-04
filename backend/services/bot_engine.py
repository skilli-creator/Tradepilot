import time
import random

def run_real_bot(config, deriv_client):

    loops = int(config.get("loops", 5))
    stake = float(config.get("stake", 1))
    market = config.get("market", "R_100")

    results = []

    # Ensure websocket is active (important)
    try:
        deriv_client.connect()
    except:
        pass

    for i in range(loops):

        # =========================
        # STEP 1: EVEN / ODD SIGNAL
        # =========================
        pick = random.randint(0, 1)

        signal_type = "EVEN" if pick == 0 else "ODD"

        contract_type = "DIGITEVEN" if signal_type == "EVEN" else "DIGITODD"

        # =========================
        # STEP 2: PROPOSAL REQUEST
        # =========================
        proposal = deriv_client.send({
            "proposal": 1,
            "amount": stake,
            "basis": "stake",
            "contract_type": contract_type,
            "currency": "USD",
            "duration": 1,
            "duration_unit": "t",
            "symbol": market
        })

        if not proposal or "error" in proposal:
            results.append({
                "error": proposal.get("error", {}).get("message", "Proposal failed")
            })
            continue

        proposal_data = proposal.get("proposal", {})

        proposal_id = proposal_data.get("id")
        ask_price = proposal_data.get("ask_price")

        if not proposal_id or not ask_price:
            results.append({"error": "Invalid proposal data"})
            continue

        # =========================
        # STEP 3: BUY CONTRACT
        # =========================
        buy_response = deriv_client.send({
            "buy": proposal_id,
            "price": ask_price
        })

        if not buy_response or "error" in buy_response:
            results.append({
                "error": buy_response.get("error", {}).get("message", "Buy failed")
            })
            continue

        contract_id = buy_response.get("buy", {}).get("contract_id")

        if not contract_id:
            results.append({"error": "No contract ID returned"})
            continue

        # =========================
        # STEP 4: MONITOR CONTRACT
        # =========================
        deriv_client.send({
            "proposal_open_contract": 1,
            "contract_id": contract_id
        })

        result = deriv_client.receive()

        contract = result.get("proposal_open_contract", {})

        profit = float(contract.get("profit", 0))
        status = "WIN" if profit > 0 else "LOSS"

        # =========================
        # STEP 5: STORE RESULT
        # =========================
        results.append({
            "market": market,
            "signal": signal_type,
            "contract_type": contract_type,
            "stake": stake,
            "profit": profit,
            "status": status
        })

        time.sleep(1)

    return results