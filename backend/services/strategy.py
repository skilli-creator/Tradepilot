import random

def generate_signal():
    confidence = random.randint(70, 95)

    direction = "BUY" if random.random() > 0.5 else "SELL"

    reason = "Momentum + volatility structure (simulated)"

    return {
        "confidence": confidence,
        "direction": direction,
        "reason": reason
    }