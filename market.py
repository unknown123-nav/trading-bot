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

        #  SAFE numeric conversion
        numeric_cols = ["open", "high", "low", "close", "vol"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

        #  ULTRA SAFE TIME FIX (KEY CHANGE)
        df["time"] = pd.to_numeric(df["time"], errors="coerce")

        # CLIP extreme values BEFORE converting
        df.loc[df["time"] > 2e12, "time"] = None

        df["time"] = pd.to_datetime(
            df["time"],
            unit="ms",
            errors="coerce"
        )

        #  remove invalid rows
        df = df.dropna(subset=["time"])

        #  final clean
        df = df.sort_values(by="time", ascending=False).reset_index(drop=True)
        df = df[["time", "open", "high", "low", "close", "vol"]]

        df["EMA20"] = (
            df["close"]
            .ewm(span=20)
            .mean()
        )
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))
        tr1 = df["high"] - df["low"]
        tr2 = abs(
            df["high"] -
            df["close"].shift()
        )
        tr3 = abs(
            df["low"] -
            df["close"].shift()
        )
        tr = pd.concat(
            [tr1, tr2, tr3],
            axis=1
        ).max(axis=1)
        df["ATR"] = tr.rolling(14).mean()
        df["NATR"] = (
            df["ATR"]
            / df["close"]
        ) * 100
        df["BB_MIDDLE"] = (
            df["close"]
            .rolling(20)
            .mean()
        )
        std = (
            df["close"]
            .rolling(20)
            .std()
        )
        df["BB_UPPER"] = (
            df["BB_MIDDLE"] + 2*std
        )
        df["BB_LOWER"] = (
            df["BB_MIDDLE"] - 2*std
        )
        df["VOLATILITY"] = (
            (df["high"] - df["low"])
            / df["close"]
        ) * 100

        ema_high_low = (
            (df["high"] - df["low"])
            .ewm(span=10)
            .mean()
        )
        df["CHAIKIN_VOL"] = (
            ema_high_low.pct_change(10)
        ) * 100
        df["VQI"] = (
            abs(df["close"]-df["open"])
            /(df["high"]-df["low"])
        )
        return df

    except Exception as e:
        print(" Market Data Error:", e)
        return pd.DataFrame()
