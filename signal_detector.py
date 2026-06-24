def interesting_signal(df):

    condition = (

        (df["POWER_SCORE"] > 60)

        &

        (df["TREND_STRENGTH"] > 0.15)

        &

        (df["SLOPE_SIGNAL"] > 1)

    )

    df["INTERESTING_SIGNAL"] = condition.astype(int)

    return df
