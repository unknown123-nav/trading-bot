import requests


API_KEY="R2J9I9NZC4TK0SRK"

def get_news(symbol):

    url=f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={API_KEY}"

    r=requests.get(url)

    data=r.json()

    if "feed" not in data:
        return None

    news=data["feed"][0]

    return {

        "headline":news["title"],

        "summary":news["summary"],

        "source":news["source"]

    }
