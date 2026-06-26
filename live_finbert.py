print("LIVE_FINBERT FILE START")
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

print("1 - Starting FinBERT import")

print("2 - Torch imported")

print("3 - Transformers imported")

MODEL = "finbert"

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

print("4 - Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(MODEL)

print("5 - Tokenizer loaded")

print("6 - Loading model...")

model = AutoModelForSequenceClassification.from_pretrained(MODEL)

print("7 - Model loaded")

model.eval()

device = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

model.to(device)

LABELS = [
    "positive",
    "negative",
    "neutral"
]

print("8 - FinBERT READY")

# ==========================================
# LIVE FINBERT
# ==========================================

def finbert_scores(news):

    if (
        news is None
        or
        "headline" not in news
    ):

        return {

            "positive":0,

            "negative":0,

            "neutral":1,

            "strength":0,

            "dominant":"NEUTRAL"

        }

    text = (
        str(news["headline"])
        + " "
        +
        str(
            news.get(
                "summary",
                ""
            )
        )
    )

    inputs = tokenizer(

        text,

        return_tensors="pt",

        truncation=True,

        max_length=128,

        padding=True

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

    strength = positive - negative

    dominant = LABELS[
        probs.argmax().item()
    ].upper()

    return {

        "positive":positive,

        "negative":negative,

        "neutral":neutral,

        "strength":strength,

        "dominant":dominant

    }
