import pandas as pd
import numpy as np


def detect_breakout(df, timeframe):

    """
    Detect breakout after a flat market.

    Returns:

    {
        "breakout": bool,
        "direction": "UP"/"DOWN"/"NONE",
        "strength": float,
        "flat_before": bool
    }
    """

    if len(df) < 20:

        return {
            "breakout": False,
            "direction": "NONE",
            "strength": 0,
            "flat_before": False
        }

    recent = df.tail(10).copy()

    latest = recent.iloc[-1]

    previous = recent.iloc[:-1]

    # ==========================================
    # FLAT MARKET
    # ==========================================

    avg_atr = previous["ATR"].mean()

    avg_trend = previous["TREND_STRENGTH"].mean()

    avg_natr = previous["NATR"].mean()

    flat_market = (

        avg_trend < 0.35

        and

        avg_natr < 1.0

    )

    # ==========================================
    # BREAKOUT SIZE
    # ==========================================

    candle_range = (

        latest["high"]

        -

        latest["low"]

    )

    average_range = (

        previous["high"]

        -

        previous["low"]

    ).mean()

    expansion = candle_range / max(average_range, 0.000001)

    # ==========================================
    # EMA BREAK
    # ==========================================

    ema_gap = abs(

        latest["EMA20"]

        -

        latest["EMA50"]

    ) / latest["EMA50"] * 100

    # ==========================================
    # PRICE MOVE
    # ==========================================

    first_close = previous.iloc[0]["close"]

    last_close = latest["close"]

    move_percent = (

        abs(last_close - first_close)

        /

        first_close

    ) * 100

    # ==========================================
    # DIRECTION
    # ==========================================

    if last_close > first_close:

        direction = "UP"

    else:

        direction = "DOWN"

    # ==========================================
    # BREAKOUT SCORE
    # ==========================================

    score = 0

    if flat_market:
        score += 30

    if expansion >= 2:
        score += 25

    elif expansion >= 1.5:
        score += 15

    if move_percent >= 1:
        score += 25

    elif move_percent >= 0.5:
        score += 15

    if ema_gap > 0.30:
        score += 20

    breakout = score >= 60

    return {

        "breakout": breakout,

        "direction": direction,

        "strength": round(score,2),

        "flat_before": flat_market,

        "move_percent": round(move_percent,2),

        "expansion": round(expansion,2)

    }
