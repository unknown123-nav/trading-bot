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

        if data.get("code") != "0" or "data" not in data:
            return pd.DataFrame()

        df = pd.DataFrame(
            data["data"],
            columns=["time", "open", "high", "low", "close", "vol", "v1", "v2", "confirm"]
        )

        if df.empty:
            return df

        # ✅ SAFE numeric conversion
        numeric_cols = ["open", "high", "low", "close", "vol"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

        # ✅ ULTRA SAFE TIME FIX (KEY CHANGE)
        df["time"] = pd.to_numeric(df["time"], errors="coerce")

        # ⚠️ CLIP extreme values BEFORE converting
        df.loc[df["time"] > 2e12, "time"] = None

        df["time"] = pd.to_datetime(
            df["time"],
            unit="ms",
            errors="coerce"
        )

        # ✅ remove invalid rows
        df = df.dropna(subset=["time"])

        # ✅ final clean
        df = df.sort_values(by="time", ascending=False).reset_index(drop=True)
        df = df[["time", "open", "high", "low", "close", "vol"]]

        return df

    except Exception as e:
        print("❌ Market Data Error:", e)
        return pd.DataFrame()
