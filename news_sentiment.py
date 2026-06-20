def classify_news_sentiment(score):

    if score>0.15:
        return "POSITIVE"

    elif score<-0.15:
        return "NEGATIVE"

    return "NEUTRAL"
