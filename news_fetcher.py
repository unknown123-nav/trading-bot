import requests
import mysql.connector
from config import DB_CONFIG

API_KEY = "9DXROO3ZY8TI1YOX"

def fetch_news(symbol, breakout_time=None):

    try:

        ticker_map = {
            "BTC-USDT": "BTC",
            "ETH-USDT": "ETH",
            "SOL-USDT": "SOL"
        }

        ticker = ticker_map.get(symbol, "BTC")

        url = (
            f"https://www.alphavantage.co/query?"
            f"function=NEWS_SENTIMENT"
            f"&tickers={ticker}"
            f"&apikey={API_KEY}"
        )

        r = requests.get(url, timeout=10)

        data = r.json()
        from datetime import datetime, timedelta

        filtered_feed = []
        feed = data.get("feed", [])
        if breakout_time is None:
            return feed[:3]
            
        for article in feed:
            try:
                published = datetime.strptime(
                    article["time_published"],
                    "%Y%m%dT%H%M%S"
                )
                published = published.replace(
    
                    tzinfo=None

                )
                breakout = breakout_time.replace(
    
                    tzinfo=None

                )
                minutes = (
                    breakout - published
                ).total_seconds() / 60
                if 0 <= minutes <= 10:
                    article["minutes_before"] = round(minutes,2)
                    filtered_feed.append(article)
            except Exception:
                pass
        return filtered_feed

    except Exception as e:

        print("News fetch error:", e)

        return []


def update_news(training_id, symbol, breakout_time=None):

    articles = fetch_news(symbol,breakout_time)

    headlines = []
    summaries = []
    sources = []

    for article in articles:

        headlines.append(
            article.get("title", "")
        )

        summaries.append(
            article.get("summary", "")
        )

        sources.append(
            article.get("source", "")
        )

    while len(headlines) < 3:

        headlines.append("NO_NEWS")
        summaries.append("NO_NEWS")
        sources.append("NONE")

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE ai_training_dataset

            SET

            headline_1=%s,
            summary_1=%s,
            source_1=%s,

            headline_2=%s,
            summary_2=%s,
            source_2=%s,

            headline_3=%s,
            summary_3=%s,
            source_3=%s

            WHERE id=%s
            """,
            (
                headlines[0],
                summaries[0],
                sources[0],

                headlines[1],
                summaries[1],
                sources[1],

                headlines[2],
                summaries[2],
                sources[2],

                training_id
            )
        )

        conn.commit()

        print(
            f"NEWS UPDATED → {symbol}"
        )

    except Exception as e:

        print("News update error:", e)

    finally:

        cursor.close()
        conn.close()
