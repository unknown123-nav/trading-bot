# ==========================================
# feature_encoder.py
# Live encoding for Manual AI
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
    "TRENDING": 0,
    "NORMAL": 1,
    "VOLATILE": 2,
    "RANGING": 3,
    "SIDEWAYS": 4
}

CANDLE_PATTERN_MAP = {
    "Bullish Candle": 0,
    "Bearish Candle": 1,
    "Bullish Engulfing": 2,
    "Bearish Engulfing": 3,
    "Doji": 4,
    "Flat": 5
}

FREQUENCY_TYPE_MAP = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2
}

SENTIMENT_MAP = {
    "POSITIVE": 0,
    "NEGATIVE": 1,
    "NEUTRAL": 2
}


def encode_pair(pair):
    return PAIR_MAP.get(pair, 0)


def encode_timeframe(timeframe):
    return TIMEFRAME_MAP.get(timeframe, 0)


def encode_market_state(state):
    return MARKET_STATE_MAP.get(state, 1)


def encode_candle(pattern):
    return CANDLE_PATTERN_MAP.get(pattern, 0)


def encode_frequency(freq):
    return FREQUENCY_TYPE_MAP.get(freq, 1)


def encode_sentiment(sentiment):
    return SENTIMENT_MAP.get(sentiment.upper(), 2)
