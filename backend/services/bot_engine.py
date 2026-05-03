def run_real_bot(config, deriv_client):

    loops = int(config["loops"])
    stake = float(config["stake"])
    market = config["market"]

    for i in range(loops):

        # STEP 1: wait market condition (you will improve this later)
        signal = "CALL"  # temporary logic

        contract = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "contract_type": signal,
                "symbol": market,
                "duration": 5,
                "duration_unit": "t"
            }
        }

        deriv_client.buy_contract(contract)