import numpy as np

# ==========================================
# POWER SCORE
# ==========================================

def calculate_power_score(df):

    latest = df.iloc[-1]

    score = 0

    # ==========================
    # EMA TREND
    # ==========================

    ema_gap = abs(
        latest["EMA20"] -
        latest["EMA50"]
    ) / latest["EMA50"] * 100

    if ema_gap > 1.5:
        score += 25

    elif ema_gap > 0.8:
        score += 18

    elif ema_gap > 0.3:
        score += 10

    # ==========================
    # RSI
    # ==========================

    rsi = latest["RSI"]

    if 45 <= rsi <= 65:
        score += 20

    elif 35 <= rsi <= 75:
        score += 12

    else:
        score += 5

    # ==========================
    # TREND STRENGTH
    # ==========================

    trend = latest["TREND_STRENGTH"]

    if trend > 2:
        score += 20

    elif trend > 1:
        score += 15

    elif trend > 0.5:
        score += 8

    # ==========================
    # CHANNEL POSITION
    # ==========================

    cp = latest["CHANNEL_POSITION"]

    if 0.25 <= cp <= 0.75:
        score += 15

    else:
        score += 6

    # ==========================
    # VOLATILITY
    # ==========================

    natr = latest["NATR"]

    if 1 <= natr <= 3:
        score += 10

    elif 0.5 <= natr <= 4:
        score += 6

    # ==========================
    # VQI
    # ==========================

    vqi = latest["VQI"]

    if vqi > 0.75:
        score += 10

    elif vqi > 0.50:
        score += 6

    # ==========================
    # LIMIT SCORE
    # ==========================

    score = max(0, min(score, 100))

    df["power_score"] = score

    return df
