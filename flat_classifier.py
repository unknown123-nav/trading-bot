# ==========================================
# MARKET STATE CLASSIFIER
# ==========================================

def market_state(df):

    latest = df.iloc[-1]

    ema20 = latest["EMA20"]
    ema50 = latest["EMA50"]

    rsi = latest["RSI"]

    trend = latest["TREND_STRENGTH"]

    natr = latest["NATR"]

    bb = latest["BB_WIDTH"]

    cp = latest["CHANNEL_POSITION"]

    # =====================================
    # BREAKOUT
    # =====================================

    if (
        trend > 2
        and
        bb > 1.5
        and
        0.80 <= cp <= 1.00
    ):

        state = "BREAKOUT"

    # =====================================
    # REVERSAL
    # =====================================

    elif (
        rsi > 75
        or
        rsi < 25
    ):

        state = "REVERSAL"

    # =====================================
    # STRONG TREND
    # =====================================

    elif (
        abs(ema20-ema50)/ema50*100 > 1
        and
        trend > 1
    ):

        state = "TRENDING"

    # =====================================
    # HIGH VOLATILITY
    # =====================================

    elif natr > 3:

        state = "VOLATILE"

    # =====================================
    # SIDEWAYS
    # =====================================

    elif bb < 0.5:

        state = "RANGING"

    # =====================================
    # NORMAL
    # =====================================

    else:

        state = "NORMAL"

    df["market_state"] = state

    return df
