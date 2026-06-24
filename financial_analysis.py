def financial_strength(df):

    df["FINANCIAL_STRENGTH"] = (

        df["POWER_SCORE"]

        *

        df["TREND_STRENGTH"]

    )

    return df
