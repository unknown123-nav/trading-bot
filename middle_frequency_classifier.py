def frequency_type(df, timeframe):

    if timeframe == "30m":

        df["FREQUENCY_TYPE"] = "MID_30M"

    elif timeframe == "1H":

        df["FREQUENCY_TYPE"] = "MID_1H"

    else:

        df["FREQUENCY_TYPE"] = "UNKNOWN"

    return df
