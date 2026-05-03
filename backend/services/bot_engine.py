import time

def run_real_bot(config, deriv_client):

    loops = int(config["loops"])
    stake = float(config["stake"])
    market = config["market"]

    results = []

    for i in range(loops):

        # =========================
        # STEP 1: REAL SIGNAL (placeholder logic)
        # =========================
        signal = "CALL"  # later we replace with AI/strategy engine

        # =========================
        # STEP 2: REQUEST PROPOSAL (REAL DERIV STEP)
        # =========================
        proposal = deriv_client.send({
            "proposal": 1,
            "amount": stake,
            "basis": "stake",
            "contract_type": signal,
            "currency": "USD",
            "duration": 5,
            "duration_unit": "t",
            "symbol": market
        })

        if "error" in proposal:
            results.append({"error": proposal["error"]["message"]})
            continue

        proposal_data = proposal["proposal"]

        proposal_id = proposal_data["id"]
        ask_price = proposal_data["ask_price"]

        # =========================
        # STEP 3: BUY CONTRACT
        # =========================
        buy_response = deriv_client.send({
            "buy": proposal_id,
            "price": ask_price
        })

        if "error" in buy_response:
            results.append({"error": buy_response["error"]["message"]})
            continue

        contract_id = buy_response["buy"]["contract_id"]

        # =========================
        # STEP 4: MONITOR CONTRACT
        # =========================
        deriv_client.send({
            "proposal_open_contract": 1,
            "contract_id": contract_id
        })

        result = deriv_client.receive()

        contract = result["proposal_open_contract"]

        profit = float(contract.get("profit", 0))

        status = "WIN" if profit > 0 else "LOSS"

        results.append({
            "market": market,
            "signal": signal,
            "stake": stake,
            "profit": profit,
            "status": status
        })

        # optional delay (avoid rate limits)
        time.sleep(1)

    return results