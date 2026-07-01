from live_finbert import finbert_scores


IMPORTANT_KEYWORDS = [

    "etf",
    "sec",
    "federal reserve",
    "fed",
    "interest rate",
    "inflation",
    "cpi",
    "bitcoin",
    "btc",
    "ethereum",
    "eth",
    "solana",
    "sol",
    "approval",
    "hack",
    "liquidation",
    "whale",
    "institution",
    "blackrock",
    "coinbase",
    "binance"

]


GOOD_SOURCES = [

    "Reuters",
    "Bloomberg",
    "CoinDesk",
    "Cointelegraph",
    "Decrypt",
    "The Block"

]


def rank_trigger_news(articles):

    if not articles:
        return None

    best = None
    best_score = -999

    for article in articles:

        title = article.get("title", "")
        summary = article.get("summary", "")

        news = {
            "headline": title,
            "summary": summary
        }

        sentiment = finbert_scores(news)

        positive = sentiment["positive"]
        negative = sentiment["negative"]

        sentiment_score = (
            positive * 2
            -
            negative
        ) * 40

        # -----------------------------
        # Timing
        # -----------------------------

        minutes = article.get("minutes_before", 10)

        if minutes <= 2:
            timing_score = 30

        elif minutes <= 5:
            timing_score = 20

        elif minutes <= 10:
            timing_score = 10

        else:
            timing_score = 0

        # -----------------------------
        # Financial keywords
        # -----------------------------

        keyword_score = 0

        text = (
            title +
            " " +
            summary
        ).lower()

        for keyword in IMPORTANT_KEYWORDS:

            if keyword in text:
                keyword_score += 5

        keyword_score = min(keyword_score, 25)

        # -----------------------------
        # Source quality
        # -----------------------------

        source = article.get("source", "")

        if source in GOOD_SOURCES:
            source_score = 15
        else:
            source_score = 5

        # -----------------------------
        # Headline Quality
        # -----------------------------

        if len(title) > 40:
            headline_score = 10
        else:
            headline_score = 5

        impact_score = (
            sentiment_score
            +
            timing_score
            +
            keyword_score
            +
            source_score
            +
            headline_score
        )

        article["impact_score"] = round(
            impact_score,
            2
        )

        article["positive"] = positive
        article["negative"] = negative
        article["keyword_score"] = keyword_score
        article["timing_score"] = timing_score
        article["source_score"] = source_score

        if impact_score > best_score:

            best_score = impact_score
            best = article

    return best
