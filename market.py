import requests
import pandas as pd

def get_data(symbol, timeframe='1m', limit=50):
    url = "https://www.okx.com/api/v5/market/candles"
    params = {
        "instId": symbol,
        "bar": timeframe,
        "limit": limit
    }

    res = requests.get(url, params=params).json()

    if res.get("code") != "0":
        return pd.DataFrame()

    df = pd.DataFrame(res["data"],
        columns=["time","open","high","low","close","vol","v1","v2","confirm"])

    df = df.astype(float)
    return df