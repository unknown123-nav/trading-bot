def classify_frequency(timeframe):

    if timeframe in ["1m","3m","5m"]:
        return "HIGH_FREQUENCY"

    elif timeframe=="15m":
        return "SHORT_SWING"

    elif timeframe in ["30m","1H"]:
        return "MIDDLE_FREQUENCY"

    else:
        return "SWING"
