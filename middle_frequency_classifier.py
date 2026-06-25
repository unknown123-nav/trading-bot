import numpy as np

# ==========================================
# SIGNAL FREQUENCY CLASSIFIER
# ==========================================

def frequency_type(df, timeframe):

    latest = df.iloc[-1]

    score = 0

    # ======================================
    # TREND STRENGTH
    # ======================================

    trend = latest["TREND_STRENGTH"]

    if trend > 2:
        score += 3

    elif trend > 1:
        score += 2

    else:
        score += 1

    # ======================================
    # RSI
    # ======================================

    rsi = latest["RSI"]

    if rsi > 70 or rsi < 30:
        score += 3

    elif rsi > 60 or rsi < 40:
        score += 2

    else:
        score += 1

    # ======================================
    # VOLATILITY
    # ======================================

    natr = latest["NATR"]

    if natr > 2:
        score += 3

    elif natr > 1:
        score += 2

    else:
        score += 1

    # ======================================
    # TIMEFRAME BONUS
    # ======================================

    tf_bonus = {
        "30m": 3,
        "1H": 4
    }

    score += tf_bonus.get(timeframe, 0)

    # ======================================
    # FINAL LABEL
    # ======================================

    if score >= 11:
        label = "HIGH"

    elif score >= 7:
        label = "MEDIUM"

    else:
        label = "LOW"

    df["FREQUENCY_TYPE"] = label

    return df
