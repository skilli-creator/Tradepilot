import random

def generate_signal(trade_type):

    confidence = random.randint(70, 95)

    if trade_type == "Rise/Fall":

        if confidence > 75:
            signal = "ENTER FALL (3–5 MIN)"
            reason = "Resistance rejection + bearish momentum detected."
        else:
            signal = "ENTER RISE (3–5 MIN)"
            reason = "Bullish momentum + support bounce detected."

    elif trade_type == "Higher/Lower":
        signal = "ENTER LOWER" if confidence > 75 else "ENTER HIGHER"
        reason = "Mean reversion pattern forming."

    elif trade_type == "Even/Odd":
        signal = "STATISTICAL EDGE DETECTED"
        reason = "Tick imbalance detected in recent data."

    else:
        signal = "ENTER TRADE"
        reason = "Volatility structure analyzed."

    return {
        "confidence": confidence,
        "signal": signal,
        "reasoning": reason
    }