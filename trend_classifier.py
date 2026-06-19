def classify_market(df):

    latest = df.iloc[0]

    adx = latest["ADX"]

    volatility = latest["VOLATILITY"]

    bb_width = (
        latest["BB_UPPER"]
        - latest["BB_LOWER"]
    ) / latest["close"] * 100

    # Strong trend
    if adx > 25:
        return "TRENDING"

    # Very volatile market
    elif volatility > 4:
        return "VOLATILE"

    # Bollinger squeeze
    elif bb_width < 2:
        return "RANGING"

    return "NORMAL"
