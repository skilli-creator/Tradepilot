def check_risk(profit, tp, sl):

    if profit >= tp:
        return "TP_HIT"

    if profit <= -sl:
        return "SL_HIT"

    return "OK"