print("MANUAL_AI_ENGINE START")
print("1")
import joblib

print("2")
import pandas as pd

print("3")
import numpy as np

print("4")
from power_score import calculate_power_score

print("5")
from financial_analysis import financial_strength

print("6")
from flat_classifier import market_state

print("7")
from middle_frequency_classifier import frequency_type

print("8")
from signal_detector import interesting_signal

print("9")
from live_finbert import finbert_scores

print("10")
from feature_encoder import encode_features

print("MANUAL_AI_ENGINE IMPORT COMPLETE")


print("========================================")
print("MANUAL AI ENGINE LOADING...")
print("========================================")

# ==========================================
# LOAD AI MODELS
# ==========================================

cat_model = joblib.load(
    "manual_catboost.pkl"
)

xgb_model = joblib.load(
    "manual_xgboost.pkl"
)

lgbm_model = joblib.load(
    "manual_lgbm.pkl"
)

print("Manual Models Loaded")

# ==========================================
# LOAD ENSEMBLE WEIGHTS
# ==========================================

CAT_WEIGHT = 0.40
XGB_WEIGHT = 0.35
LGBM_WEIGHT = 0.25

BUY_THRESHOLD = 0.40
SELL_THRESHOLD = 0.40

# ==========================================
# LOAD BUY / SELL THRESHOLDS
# ==========================================


print(
    f"BUY Threshold : {BUY_THRESHOLD}"
)

print(
    f"SELL Threshold : {SELL_THRESHOLD}"
)

FEATURES = [

"EMA20",
"EMA50",
"RSI",
"ATR",
"NATR",

"BB_WIDTH",
"CHAIKIN_VOL",
"VQI",

"TREND_STRENGTH",
"CHANNEL_POSITION",

"SLOPE_SIGNAL",
"POWER_SCORE",

"ACTIVE_PASSIVE",

"FINANCIAL_STRENGTH",

"pair",
"timeframe",

"MARKET_STATE",

"CANDLE_PATTERN",

"FREQUENCY_TYPE",

"h1_positive",
"h1_negative",
"h1_neutral",

"h2_positive",
"h2_negative",
"h2_neutral",

"h3_positive",
"h3_negative",
"h3_neutral",

"overall_positive",
"overall_negative",
"overall_neutral",

"news_strength",

"dominant_sentiment"

]
print(
    "Manual AI Ready"
)

# ==========================================
# LIVE MANUAL AI
# ==========================================

def predict_manual_trade(

        df,

        pair,

        timeframe,

        news

):

    if df.empty:

        return None

    # ======================================
    # POWER SCORE
    # ======================================

    df = calculate_power_score(
        df
    )

    # ======================================
    # FINANCIAL STRENGTH
    # ======================================

    df = financial_strength(
        df
    )

    # ======================================
    # MARKET STATE
    # ======================================

    df = market_state(
        df
    )

    # ======================================
    # FREQUENCY TYPE
    # ======================================

    df = frequency_type(
        df,
        timeframe
    )

    # ======================================
    # INTERESTING SIGNAL
    # ======================================

    df = interesting_signal(
        df
    )

    # ======================================
    # IDENTIFIERS
    # ======================================

    df["pair"] = pair

    df["timeframe"] = timeframe

    # ======================================
    # LATEST CANDLE
    # ======================================

    latest = df.tail(1).copy()

    # ======================================
    # FINBERT
    # ======================================

    sentiment = finbert_scores(news)
    latest["h1_positive"] = sentiment["positive"]
    latest["h1_negative"] = sentiment["negative"]
    latest["h1_neutral"] = sentiment["neutral"]
    latest["h2_positive"] = sentiment["positive"]
    latest["h2_negative"] = sentiment["negative"]
    latest["h2_neutral"] = sentiment["neutral"]
    latest["h3_positive"] = sentiment["positive"]
    latest["h3_negative"] = sentiment["negative"]
    latest["h3_neutral"] = sentiment["neutral"]
    latest["overall_positive"] = sentiment["positive"]
    latest["overall_negative"] = sentiment["negative"]
    latest["overall_neutral"] = sentiment["neutral"]
    latest["news_strength"] = sentiment["strength"]
    latest["dominant_sentiment"] = sentiment["dominant"]


    # ======================================
    # SAFETY
    # ======================================

    latest.replace(

        [np.inf, -np.inf],

        0,

        inplace=True

    )

    latest.fillna(

        0,

        inplace=True

    )

    # ======================================
    # FEATURE ENCODING
    # ======================================

    latest = encode_features(
        latest
    )

    # ======================================
    # VERIFY FEATURES
    # ======================================

    missing = [

        col

        for col in FEATURES

        if col not in latest.columns

    ]

    if missing:

        raise ValueError(

            f"Missing Features : {missing}"

        )

    print("\n================ FEATURES IN DATAFRAME ================")
    print(latest.columns.tolist())
    print("\n================ MODEL FEATURES ================")
    print(FEATURES)
    print("\n================ X COLUMNS ================")
    X = latest[FEATURES]
    print(X.columns.tolist())
    print("\n================ FIRST ROW ================")
    print(X.iloc[0])

    # ======================================
    # CATBOOST
    # ======================================

    cat_probability = float(

        cat_model.predict_proba(
            X
        )[0][1]

    )

    # ======================================
    # XGBOOST
    # ======================================

    xgb_probability = float(

        xgb_model.predict_proba(
            X
        )[0][1]

    )

    # ======================================
    # LIGHTGBM
    # ======================================

    lgb_probability = float(

        lgbm_model.predict_proba(
            X
        )[0][1]

    )

    # ======================================
    # DYNAMIC ENSEMBLE
    # ======================================

    probability = (

        CAT_WEIGHT * cat_probability

        +

        XGB_WEIGHT * xgb_probability

        +

        LGBM_WEIGHT * lgb_probability

    )

    probability = float(

        np.clip(
            probability,
            0,
            1
        )

    )

    confidence = round(

        probability * 100,

        2

    )

    print()

    print("========== MANUAL AI ==========")

    print("Pair :", pair)

    print("Timeframe :", timeframe)

    print()

    print("CatBoost :", round(cat_probability,4))

    print("XGBoost :", round(xgb_probability,4))

    print("LightGBM :", round(lgb_probability,4))

    print()

    print("Ensemble :", round(probability,4))

    print("Confidence :", confidence)

    print()

    print("===============================")

    # ======================================
    # FINAL SIGNAL
    # ======================================

    if probability >= BUY_THRESHOLD:

        signal = "BUY"

    elif probability <= SELL_THRESHOLD:

        signal = "SELL"

    else:

        signal = "NO TRADE"

    # ======================================
    # SIGNAL STRENGTH
    # ======================================

    if probability >= 0.90:

        strength = "VERY STRONG"

    elif probability >= 0.80:

        strength = "STRONG"

    elif probability >= BUY_THRESHOLD:

        strength = "MODERATE"

    elif probability <= SELL_THRESHOLD:

        strength = "STRONG SELL"

    else:

        strength = "NEUTRAL"

    # ======================================
    # INTERESTING SIGNAL
    # ======================================

    interesting = bool(

        latest.iloc[0][

            "INTERESTING_SIGNAL"

        ]

    )

    # ======================================
    # OUTPUT
    # ======================================

    result = {

        "signal": signal,

        "strength": strength,

        "confidence": confidence,

        "probability": probability,

        "buy_threshold": BUY_THRESHOLD,

        "sell_threshold": SELL_THRESHOLD,

        "catboost": round(

            cat_probability,

            4

        ),

        "xgboost": round(

            xgb_probability,

            4

        ),

        "lightgbm": round(

            lgb_probability,

            4

        ),

        "interesting_signal": interesting,

        "power_score": float(

            latest.iloc[0][

                "POWER_SCORE"

            ]

        ),

        "financial_strength": float(

            latest.iloc[0][

                "FINANCIAL_STRENGTH"

            ]

        ),

        "market_state": latest.iloc[0][

            "MARKET_STATE"

        ],

        "frequency_type": latest.iloc[0][

            "FREQUENCY_TYPE"

        ],

        "candle_type": latest.iloc[0]["CANDLE_PATTERN"],



        "positive_news": float(

            latest.iloc[0][

                "overall_positive"

            ]

        ),

        "negative_news": float(

            latest.iloc[0][

                "overall_negative"

            ]

        ),

        "neutral_news": float(

            latest.iloc[0][

                "overall_neutral"

            ]

        ),

        "news_strength": float(

            latest.iloc[0][

                "news_strength"

            ]

        ),

        "dominant_sentiment": latest.iloc[0][

            "dominant_sentiment"

        ]

    }



# ==========================================
# DEBUG OUTPUT
# ==========================================

    print()

    print("============== MANUAL AI RESULT ==============")

    print("Signal              :", result["signal"])
    print("Strength            :", result["strength"])
    print("Confidence          :", result["confidence"])
    print("Probability         :", round(result["probability"],4))

    print()

    print("BUY Threshold       :", BUY_THRESHOLD)
    print("SELL Threshold      :", SELL_THRESHOLD)

    print()

    print("Power Score         :", result["power_score"])
    print("Financial Strength  :", result["financial_strength"])

    print()

    print("Market State        :", result["market_state"])
    print("Frequency           :", result["frequency_type"])
    print("Candle              :", result["candle_type"])

    print()

    print("Interesting Signal  :", result["interesting_signal"])

    print()

    print("Positive News       :", round(result["positive_news"],4))
    print("Negative News       :", round(result["negative_news"],4))
    print("Neutral News        :", round(result["neutral_news"],4))
    print("News Strength       :", round(result["news_strength"],4))
    print("Sentiment           :", result["dominant_sentiment"])

    print()

    print("CatBoost            :", round(result["catboost"],4))
    print("XGBoost             :", round(result["xgboost"],4))
    print("LightGBM            :", round(result["lightgbm"],4))

    print("=============================================")

    return result


# ==========================================
# FAIL SAFE
# ==========================================

def safe_predict_manual_trade(
        df,
        pair,
        timeframe,
        news
):

    try:

        result = predict_manual_trade(
            df,
            pair,
            timeframe,
            news
        )

        if result is None:

            return None

        if np.isnan(result["probability"]):

            print("Probability is NaN")

            return None

        if np.isinf(result["probability"]):

            print("Probability is Infinite")

            return None
            
        return result

        

    except Exception as e:

        print()

        print("MANUAL AI ERROR")

        print(e)

        print()

        return {

            "signal":"NO TRADE",

            "strength":"ERROR",

            "confidence":0,

            "probability":0,

            "buy_threshold":BUY_THRESHOLD,

            "sell_threshold":SELL_THRESHOLD,

            "catboost":0,

            "xgboost":0,

            "lightgbm":0,

            "interesting_signal":False,

            "power_score":0,

            "financial_strength":0,

            "market_state":"UNKNOWN",

            "frequency_type":"UNKNOWN",

            "candle_type":"UNKNOWN",

            "positive_news":0,

            "negative_news":0,

            "neutral_news":0,

            "news_strength":0,

            "dominant_sentiment":"UNKNOWN"

        }

