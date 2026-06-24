import numpy as np

def calculate_power_score(df):

    body = abs(
        df["close"] -
        df["open"]
    )

    rng = (
        df["high"] -
        df["low"]
    )

    volume_factor = (
        df["vol"] /
        (
            df["vol"]
            .rolling(20)
            .mean()
            + 1e-8
        )
    )

    score = (
        body /
        (rng + 1e-8)
    ) * 100

    df["POWER_SCORE"] = (
        score * 0.70
        +
        volume_factor * 30
    )

    return df
