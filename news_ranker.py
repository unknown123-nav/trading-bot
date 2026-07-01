from live_finbert import finbert_scores


def rank_trigger_news(articles):

    if not articles:
        return None

    best = None
    best_score = -999

    for article in articles:

        news = {
            "headline": article.get("title", ""),
            "summary": article.get("summary", "")
        }

        sentiment = finbert_scores(news)

        positive = sentiment["positive"]
        negative = sentiment["negative"]
        neutral = sentiment["neutral"]

        # =====================================
        # Sentiment Score
        # =====================================

        sentiment_score = (
            positive * 2
            - negative
        ) * 40

        # =====================================
        # Timing Score
        # News closer to breakout = higher score
        # =====================================

        minutes = article.get("minutes_before", 10)

        if minutes <= 2:
            timing_score = 30

        elif minutes <= 5:
            timing_score = 20

        elif minutes <= 10:
            timing_score = 10

        else:
            timing_score = 0

        # =====================================
        # Headline Length Score
        # =====================================

        headline = article.get("title", "")

        if len(headline) > 40:
            headline_score = 10
        else:
            headline_score = 5

        # =====================================
        # Total Impact Score
        # =====================================

        impact_score = (
            sentiment_score
            + timing_score
            + headline_score
        )

        article["impact_score"] = round(impact_score, 2)

        article["positive"] = positive
        article["negative"] = negative
        article["neutral"] = neutral

        if impact_score > best_score:

            best_score = impact_score
            best = article

    return best
