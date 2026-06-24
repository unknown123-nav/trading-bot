from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

import torch
import numpy as np

MODEL_NAME = "ProsusAI/finbert"

print("Loading FinBERT...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME
)

device = "cuda" if torch.cuda.is_available() else "cpu"

model.to(device)

model.eval()

print("FinBERT Ready")
def analyse(text):

    if text is None:
        text = "NO_NEWS"

    if text == "":
        text = "NO_NEWS"

    inputs = tokenizer(

        text,

        return_tensors="pt",

        truncation=True,

        padding=True,

        max_length=128

    )

    inputs = {

        k:v.to(device)

        for k,v in inputs.items()

    }

    with torch.no_grad():

        outputs = model(**inputs)

        probs = torch.softmax(

            outputs.logits,

            dim=1

        )[0]

    positive = float(probs[0])

    negative = float(probs[1])

    neutral = float(probs[2])

    return positive,negative,neutral

def analyse_news(news):

    headlines = []

    for item in news:

        headlines.append(
            item["headline"]
        )

    while len(headlines) < 3:

        headlines.append(
            "NO_NEWS"
        )

    p1,n1,u1 = analyse(headlines[0])

    p2,n2,u2 = analyse(headlines[1])

    p3,n3,u3 = analyse(headlines[2])

    overall_positive = (

        p1+p2+p3

    )/3

    overall_negative = (

        n1+n2+n3

    )/3

    overall_neutral = (

        u1+u2+u3

    )/3

    news_strength = (

        overall_positive

        -

        overall_negative

    )

    values = {

        "h1_positive":p1,
        "h1_negative":n1,
        "h1_neutral":u1,

        "h2_positive":p2,
        "h2_negative":n2,
        "h2_neutral":u2,

        "h3_positive":p3,
        "h3_negative":n3,
        "h3_neutral":u3,

        "overall_positive":overall_positive,
        "overall_negative":overall_negative,
        "overall_neutral":overall_neutral,

        "news_strength":news_strength

    }

    sentiment = {

        "POSITIVE":overall_positive,

        "NEGATIVE":overall_negative,

        "NEUTRAL":overall_neutral

    }

    values["dominant_sentiment"] = max(

        sentiment,

        key=sentiment.get

    )

    return values
