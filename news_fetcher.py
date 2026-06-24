import requests

API_KEY = "R2J9I9NZC4TK0SRK"


def get_news(symbol):

    symbol = symbol.replace("-USDT","")

    url = (
        "https://www.alphavantage.co/query?"
        f"function=NEWS_SENTIMENT"
        f"&tickers={symbol}"
        f"&apikey={API_KEY}"
    )

    r = requests.get(url)

    data = r.json()

    if "feed" not in data:

        return {
            "headline":"NO_NEWS",
            "summary":"NO_NEWS",
            "source":"NONE"
        }

    article = data["feed"][0]

    return {

        "headline":article["title"],

        "summary":article["summary"],

        "source":article["source"]

    }
