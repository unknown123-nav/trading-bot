import pandas as pd

def atr_instability(df):

    current_atr = df.iloc[0]["ATR"]

    avg_atr = (
        df["ATR"]
        .head(20)
        .mean()
    )

    ratio = current_atr / avg_atr

    unstable = ratio > 1.5

    return unstable, ratio

def donchian_channel(df):

    upper = (
        df["high"]
        .head(20)
        .max()
    )

    lower = (
        df["low"]
        .head(20)
        .min()
    )

    width = upper - lower

    return upper, lower, width

