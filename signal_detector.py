def detect_signal_class(
        direction,
        trend_strength,
        volatility,
        candle_type
):

    if candle_type=="Bullish Engulfing":
        return "Bullish Breakout"

    if candle_type=="Bearish Engulfing":
        return "Bearish Breakout"

    if volatility>4:
        return "Volatility Spike"

    if trend_strength>1:
        return "Power Move"

    return "Trend Continuation"
