import numpy as np

def market_state(df):

    df["MARKET_STATE"] = "NORMAL"

    df.loc[
        df["TREND_STRENGTH"] > 0.20,
        "MARKET_STATE"
    ] = "TRENDING"

    df.loc[
        df["BB_WIDTH"] < 0.50,
        "MARKET_STATE"
    ] = "RANGING"

    return df
