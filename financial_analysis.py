import numpy as np

# ==========================================
# FINANCIAL STRENGTH
# ==========================================

def financial_strength(df):

    latest = df.iloc[-1]

    score = 0

    # ==================================
    # TREND STRENGTH
    # ==================================

    trend = latest["TREND_STRENGTH"]

    if trend > 2:
        score += 25

    elif trend > 1:
        score += 18

    elif trend > 0.5:
        score += 10

    # ==================================
    # RSI
    # ==================================

    rsi = latest["RSI"]

    if 45 <= rsi <= 65:
        score += 15

    elif 35 <= rsi <= 75:
        score += 10

    else:
        score += 5

    # ==================================
    # VOLATILITY
    # ==================================

    natr = latest["NATR"]

    if 1 <= natr <= 3:
        score += 15

    elif 0.5 <= natr <= 4:
        score += 8

    # ==================================
    # CHAIKIN VOLATILITY
    # ==================================

    chaikin = latest["CHAIKIN_VOL"]

    if chaikin > 10:
        score += 10

    elif chaikin > 3:
        score += 6

    # ==================================
    # VQI
    # ==================================

    vqi = latest["VQI"]

    if vqi > 0.75:
        score += 10

    elif vqi > 0.50:
        score += 6

    # ==================================
    # EMA TREND
    # ==================================

    ema_gap = abs(
        latest["EMA20"] -
        latest["EMA50"]
    ) / latest["EMA50"] * 100

    if ema_gap > 1.5:
        score += 10

    elif ema_gap > 0.7:
        score += 5

    # ==================================
    # BOLLINGER WIDTH
    # ==================================

    width = latest["BB_WIDTH"]

    if width > 0:
        score += 5

    # ==================================
    # LIMIT
    # ==================================

    score = max(0, min(score, 100))

    df["FINANCIAL_STRENGTH"] = score

    return df
