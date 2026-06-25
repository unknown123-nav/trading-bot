import pandas as pd

# ==========================================
# FIXED ENCODERS
# ==========================================

PAIR_MAP = {
    "BTC-USDT": 0,
    "ETH-USDT": 1,
    "SOL-USDT": 2
}

TIMEFRAME_MAP = {
    "30m": 0,
    "1H": 1
}

MARKET_STATE_MAP = {
    "RANGING": 0,
    "NORMAL": 1,
    "TRENDING": 2,
    "BREAKOUT": 3,
    "REVERSAL": 4,
    "VOLATILE": 5
}

CANDLE_PATTERN_MAP = {
    "Doji": 0,
    "Bullish Candle": 1,
    "Bearish Candle": 2,
    "Bullish Engulfing": 3,
    "Bearish Engulfing": 4,
    "Hammer": 5,
    "Shooting Star": 6,
    "Flat": 7
}

FREQUENCY_MAP = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2
}

SENTIMENT_MAP = {
    "NEGATIVE": 0,
    "NEUTRAL": 1,
    "POSITIVE": 2
}

# ==========================================
# ENCODE
# ==========================================

def encode_features(df):

    df = df.copy()

    df["pair"] = (
        df["pair"]
        .map(PAIR_MAP)
        .fillna(-1)
        .astype(int)
    )

    df["timeframe"] = (
        df["timeframe"]
        .map(TIMEFRAME_MAP)
        .fillna(-1)
        .astype(int)
    )

    df["market_state"] = (
        df["market_state"]
        .map(MARKET_STATE_MAP)
        .fillna(-1)
        .astype(int)
    )

    df["CANDLE_PATTERN"] = (
        df["CANDLE_PATTERN"]
        .map(CANDLE_PATTERN_MAP)
        .fillna(-1)
        .astype(int)
    )

    df["frequency_type"] = (
        df["frequency_type"]
        .map(FREQUENCY_MAP)
        .fillna(-1)
        .astype(int)
    )

    df["dominant_sentiment"] = (
        df["dominant_sentiment"]
        .str.upper()
        .map(SENTIMENT_MAP)
        .fillna(1)
        .astype(int)
    )

    return df
