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

        score = (
            sentiment["positive"] * 2
            - sentiment["negative"]
        )

        article["impact_score"] = score

        if score > best_score:

            best_score = score

            best = article

    return best
