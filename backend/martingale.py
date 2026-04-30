def next_stake(current, base, martingale_on, max_limit=8):

    if not martingale_on:
        return base

    next_value = current * 2

    # safety cap
    if next_value > base * max_limit:
        return base

    return next_value