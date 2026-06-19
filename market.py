import requests
import pandas as pd


def get_data(symbol, timeframe="1m", limit=50):

    try:

        url = "https://www.okx.com/api/v5/market/candles"

        params = {
            "instId": symbol,
            "bar": timeframe,
            "limit": limit
        }

        response = requests.get(
            url,
            params=params,
            timeout=5
        )

        data = response.json()

        if data.get("code") != "0" or "data" not in data:
            return pd.DataFrame()

        df = pd.DataFrame(
            data["data"],
            columns=[
                "time",
                "open",
                "high",
                "low",
                "close",
                "vol",
                "v1",
                "v2",
                "confirm"
            ]
        )

        if df.empty:
            return df

        # ======================
        # NUMERIC CONVERSION
        # ======================

        numeric_cols = [
            "open",
            "high",
            "low",
            "close",
            "vol"
        ]

        df[numeric_cols] = (
            df[numeric_cols]
            .apply(pd.to_numeric, errors="coerce")
        )

        # ======================
        # TIME
        # ======================

        df["time"] = pd.to_numeric(
            df["time"],
            errors="coerce"
        )

        df.loc[df["time"] > 2e12, "time"] = None

        df["time"] = pd.to_datetime(
            df["time"],
            unit="ms",
            errors="coerce"
        )

        df = df.dropna(subset=["time"])

        df = (
            df.sort_values(
                by="time",
                ascending=False
            )
            .reset_index(drop=True)
        )

        df = df[
            [
                "time",
                "open",
                "high",
                "low",
                "close",
                "vol"
            ]
        ]

        # ======================
        # EMA20
        # ======================

        df["EMA20"] = (
            df["close"]
            .ewm(
                span=20,
                adjust=False
            )
            .mean()
        )

        # ======================
        # EMA50
        # ======================

        df["EMA50"] = (
            df["close"]
            .ewm(
                span=50,
                adjust=False
            )
            .mean()
        )

        # ======================
        # RSI
        # ======================

        delta = df["close"].diff()

        gain = delta.clip(lower=0)

        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()

        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss

        df["RSI"] = 100 - (
            100 / (1 + rs)
        )

        # ======================
        # ATR
        # ======================

        tr1 = (
            df["high"] -
            df["low"]
        )

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

        df["ATR"] = (
            tr
            .rolling(14)
            .mean()
        )

        # ======================
        # NATR
        # ======================

        df["NATR"] = (
            df["ATR"]
            / df["close"]
        ) * 100

        # ======================
        # BOLLINGER BANDS
        # ======================

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
            df["BB_MIDDLE"]
            + 2 * std
        )

        df["BB_LOWER"] = (
            df["BB_MIDDLE"]
            - 2 * std
        )

        # ======================
        # VOLATILITY
        # ======================

        df["VOLATILITY"] = (
            (
                df["high"]
                - df["low"]
            )
            / df["close"]
        ) * 100

        # ======================
        # MACD
        # ======================

        ema12 = (
            df["close"]
            .ewm(
                span=12,
                adjust=False
            )
            .mean()
        )

        ema26 = (
            df["close"]
            .ewm(
                span=26,
                adjust=False
            )
            .mean()
        )

        df["MACD"] = (
            ema12 - ema26
        )

        df["MACD_SIGNAL"] = (
            df["MACD"]
            .ewm(
                span=9,
                adjust=False
            )
            .mean()
        )

        # ======================
        # ADX
        # ======================

        plus_dm = (
            df["high"]
            .diff()
        )

        minus_dm = (
            -df["low"]
            .diff()
        )

        plus_dm[
            plus_dm < 0
        ] = 0

        minus_dm[
            minus_dm < 0
        ] = 0

        plus_di = (
            100
            * plus_dm
            .rolling(14)
            .mean()
            / (
                df["ATR"]
                + 1e-5
            )
        )

        minus_di = (
            100
            * minus_dm
            .rolling(14)
            .mean()
            / (
                df["ATR"]
                + 1e-5
            )
        )

        dx = (
            abs(
                plus_di
                - minus_di
            )
            /
            (
                plus_di
                + minus_di
                + 1e-5
            )
        ) * 100

        df["ADX"] = (
            dx
            .rolling(14)
            .mean()
        )

        # ======================
        # CHAIKIN VOLATILITY
        # ======================

        ema_range = (
            (
                df["high"]
                - df["low"]
            )
            .ewm(
                span=10,
                adjust=False
            )
            .mean()
        )

        df["CHAIKIN_VOL"] = (
            ema_range
            .pct_change(10)
        ) * 100

        # ======================
        # VQI
        # ======================

        df["VQI"] = (
            abs(
                df["close"]
                - df["open"]
            )
            /
            (
                df["high"]
                - df["low"]
                + 1e-5
            )
        )

        return df

    except Exception as e:

        print(
            "Market Data Error:",
            e
        )

        return pd.DataFrame()
