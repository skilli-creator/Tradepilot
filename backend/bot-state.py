class BotState:
    running = False

    profit = 0.0
    wins = 0
    losses = 0
    trades = 0

    confidence = 0
    reasoning = ""

    current_stake = 0

    # NEW
    last_contract_id = None