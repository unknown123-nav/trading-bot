import requests
import pandas as pd


def get_data(symbol, timeframe='1m', limit=50):
    try:
        url = "https://www.okx.com/api/v5/market/candles"

        params = {
            "instId": symbol,
            "bar": timeframe,
            "limit": limit
        }

        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        # ✅ Check response
        if data.get("code") != "0" or "data" not in data:
            return pd.DataFrame()

        # ✅ Create DataFrame
        df = pd.DataFrame(
            data["data"],
            columns=["time", "open", "high", "low", "close", "vol", "v1", "v2", "confirm"]
        )

        if df.empty:
            return df

        # ✅ Convert types (IMPORTANT fix)
        numeric_cols = ["open", "high", "low", "close", "vol"]
        df[numeric_cols] = df[numeric_cols].astype(float)

        # ✅ Convert timestamp
        df["time"] = pd.to_datetime(df["time"], unit="ms")

        # ✅ Sort newest → oldest (your AI expects this)
        df = df.sort_values(by="time", ascending=False).reset_index(drop=True)

        # ✅ Keep only needed columns (clean)
        df = df[["time", "open", "high", "low", "close", "vol"]]

        return df

    except Exception as e:
        print("❌ Market Data Error:", e)
        return pd.DataFrame()
