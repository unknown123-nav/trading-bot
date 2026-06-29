import numpy as np


def detect_breakout(df):

    if len(df) < 12:
        return False

    recent = df.tail(10)

    # Average range of previous candles
    avg_range = (
        (recent["high"] - recent["low"])
        .head(9)
        .mean()
    )

    # Latest candle
    latest = recent.iloc[-1]

    latest_range = latest["high"] - latest["low"]

    # Trend before breakout
    ema_gap = abs(
        latest["EMA20"] -
        latest["EMA50"]
    ) / latest["EMA50"] * 100

    trend = latest["TREND_STRENGTH"]

    # Previous market should be flat
    was_flat = trend < 0.40 and ema_gap < 0.30

    # Breakout candle should be much larger
    breakout = latest_range > avg_range * 2

    return was_flat and breakout
