def classify_market(df):

    latest = df.iloc[0]

    adx = latest["ADX"]

    volatility = latest["VOLATILITY"]

    bb_width = (
        latest["BB_UPPER"]
        - latest["BB_LOWER"]
    ) / latest["close"] * 100

    macd = latest["MACD"]
    signal = latest["MACD_SIGNAL"]

    ema20 = latest["EMA20"]
    ema50 = latest["EMA50"]

    # Strong trend
    if (
        adx > 25
        and abs(macd - signal) > 0
        and abs(ema20 - ema50)/ema50*100 > 0.15
    ):
        return "TRENDING"

    # Volatile market
    elif volatility > 4:
        return "VOLATILE"

    # Bollinger squeeze
    elif bb_width < 2:
        return "RANGING"

    # Sideways
    elif adx < 18:
        return "SIDEWAYS"

    return "NORMAL"
