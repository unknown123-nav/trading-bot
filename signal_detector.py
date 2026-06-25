import numpy as np

# ==========================================
# SLOPE SIGNAL
# ==========================================

def slope_signal(df):

    closes = df["close"].tail(3).values

    x = np.arange(3)

    slope = np.polyfit(
        x,
        closes,
        1
    )[0]

    pct = (
        slope /
        closes[-1]
    ) * 100

    if pct >= 0.40:
        return 4

    elif pct >= 0.20:
        return 3

    elif pct >= 0.05:
        return 2

    elif pct > -0.05:
        return 1

    elif pct > -0.20:
        return -1

    elif pct > -0.40:
        return -2

    else:
        return -3


# ==========================================
# ACTIVE / PASSIVE
# ==========================================

def active_passive(df):

    latest = df.iloc[-1]

    score = 0

    if latest["NATR"] > 2:
        score += 1

    if latest["CHAIKIN_VOL"] > 5:
        score += 1

    if latest["TREND_STRENGTH"] > 1:
        score += 1

    if latest["VQI"] > 0.70:
        score += 1

    return score


# ==========================================
# CANDLE PATTERN
# ==========================================

def candle_pattern(df):

    latest = df.iloc[-1]

    body = abs(
        latest["close"] -
        latest["open"]
    )

    rng = (
        latest["high"] -
        latest["low"]
    )

    if rng == 0:
        return "Flat"

    if body <= rng * 0.10:
        return "Doji"

    if latest["close"] > latest["open"]:
        return "Bullish Candle"

    return "Bearish Candle"


# ==========================================
# INTERESTING SIGNAL
# ==========================================

def interesting_signal(df):

    latest = df.iloc[-1]

    score = 0

    if latest["TREND_STRENGTH"] > 1:
        score += 2

    if latest["NATR"] > 2:
        score += 2

    if latest["RSI"] < 30 or latest["RSI"] > 70:
        score += 2

    if latest["VQI"] > 0.70:
        score += 2

    if latest["CHANNEL_POSITION"] > 0.85:
        score += 1

    if latest["CHANNEL_POSITION"] < 0.15:
        score += 1

    df["INTERESTING_SIGNAL"] = int(score >= 5)

    df["SIGNAL_SCORE"] = score

    df["SLOPE_SIGNAL"] = slope_signal(df)

    df["ACTIVE_PASSIVE"] = active_passive(df)

    df["CANDLE_PATTERN"] = candle_pattern(df)

    return df
