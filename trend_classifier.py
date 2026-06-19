def classify_market(df):

    latest = df.iloc[0]

    trend_strength = latest["TREND_STRENGTH"]
    natr = latest["NATR"]
    bb_width = latest["BB_WIDTH"]

    # Strong trend
    if trend_strength > 0.30:
        return "TRENDING"

    # High volatility
    elif natr > 2:
        return "VOLATILE"

    # Range market
    elif bb_width < 2:
        return "RANGING"

    return "NORMAL"
