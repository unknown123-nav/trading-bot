import numpy as np


# ==========================================
# CANDLE PATTERN
# ==========================================

def candle_pattern(df):

    latest = df.iloc[-1]

    body = abs(
        latest["close"] -
        latest["open"]
    )

    candle_range = (
        latest["high"] -
        latest["low"]
    )

    upper_shadow = (
        latest["high"] -
        max(
            latest["close"],
            latest["open"]
        )
    )

    lower_shadow = (
        min(
            latest["close"],
            latest["open"]
        )
        -
        latest["low"]
    )

    if candle_range == 0:
        return "FLAT"

    body_ratio = body / candle_range

    if body_ratio < 0.10:
        return "DOJI"

    if (
        lower_shadow >
        body * 2
        and
        upper_shadow < body
    ):
        return "HAMMER"

    if (
        upper_shadow >
        body * 2
        and
        lower_shadow < body
    ):
        return "SHOOTING_STAR"

    if latest["close"] > latest["open"]:
        return "BULLISH"

    return "BEARISH"


# ==========================================
# 3 BAR SLOPE
# ==========================================

def slope_signal(df):

    closes = (
        df["close"]
        .tail(3)
        .values
    )

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

    if pct > 0.30:
        return "STRONG_UP"

    elif pct > 0.10:
        return "UP"

    elif pct < -0.30:
        return "STRONG_DOWN"

    elif pct < -0.10:
        return "DOWN"

    else:
        return "FLAT"


# ==========================================
# TREND DIRECTION
# ==========================================

def trend_direction(df):

    latest = df.iloc[-1]

    if latest["EMA20"] > latest["EMA50"]:
        return "UP"

    elif latest["EMA20"] < latest["EMA50"]:
        return "DOWN"

    return "SIDEWAYS"


# ==========================================
# INTERESTING SIGNAL
# ==========================================

def interesting_signal(df):

    latest = df.iloc[-1]

    score = 0

    # RSI

    if latest["RSI"] < 30:

        score += 2

    elif latest["RSI"] > 70:

        score += 2

    # Volatility

    if latest["NATR"] > 2:

        score += 2

    # Trend

    if latest["TREND_STRENGTH"] > 1:

        score += 2

    # Bollinger Width

    if latest["BB_WIDTH"] > 1:

        score += 1

    # Chaikin

    if abs(
        latest["CHAIKIN_VOL"]
    ) > 10:

        score += 1

    signal = int(score >= 5)

    df["INTERESTING_SIGNAL"] = signal

    df["SIGNAL_SCORE"] = score

    df["SLOPE_SIGNAL"] = slope_signal(df)

    df["CANDLE_PATTERN"] = candle_pattern(df)

    df["TREND_DIRECTION"] = trend_direction(df)

    return df
