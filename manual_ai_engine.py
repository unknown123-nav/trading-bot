import os
import joblib
import numpy as np
import pandas as pd

from power_score import calculate_power_score
from financial_analysis import financial_strength
from flat_classifier import market_state
from middle_frequency_classifier import frequency_type
from signal_detector import interesting_signal

from live_finbert import finbert_scores
from feature_encoder import encode_features

print("MANUAL AI ENGINE LOADED")

# ==========================================
# LOAD MODELS
# ==========================================

cat_model = joblib.load("manual_catboost.pkl")
xgb_model = joblib.load("manual_xgboost.pkl")
lgbm_model = joblib.load("manual_lgbm.pkl")
threshold = joblib.load("ensemble_threshold.pkl")

print("Manual Models Loaded")

# ==========================================
# FEATURE LIST (MATCH TRAINING EXACTLY)
# ==========================================

FEATURES = [
    "EMA20", "EMA50", "RSI", "ATR", "NATR",
    "BB_WIDTH", "CHAIKIN_VOL", "VQI",
    "TREND_STRENGTH", "CHANNEL_POSITION",
    "SLOPE_SIGNAL", "POWER_SCORE",
    "ACTIVE_PASSIVE",
    "FINANCIAL_STRENGTH",
    "pair", "timeframe",
    "MARKET_STATE", "CANDLE_PATTERN",
    "FREQUENCY_TYPE",
    "h1_positive", "h1_negative", "h1_neutral",
    "h2_positive", "h2_negative", "h2_neutral",
    "h3_positive", "h3_negative", "h3_neutral",
    "overall_positive", "overall_negative", "overall_neutral",
    "news_strength",
    "dominant_sentiment"
]

# ==========================================
# MAIN PREDICTION FUNCTION
# ==========================================

def predict_manual_trade(df, pair, timeframe, news):

    # ============================
    # FEATURE ENGINEERING PIPELINE
    # ============================

    df = calculate_power_score(df)
    df = financial_strength(df)
    df = market_state(df)
    df = frequency_type(df, timeframe)
    df = interesting_signal(df)

    # Add identifiers
    df["pair"] = pair
    df["timeframe"] = timeframe

    # ============================
    # GET LATEST ROW
    # ============================

    latest = df.iloc[-1:].copy()

    # ============================
    # SENTIMENT ANALYSIS
    # ============================

    sentiment = finbert_scores(news)

    latest["overall_positive"] = sentiment["positive"]
    latest["overall_negative"] = sentiment["negative"]
    latest["overall_neutral"] = sentiment["neutral"]
    latest["news_strength"] = sentiment["strength"]
    latest["dominant_sentiment"] = sentiment["dominant"]

    # ============================
    # ENCODE FEATURES
    # ============================

    latest = encode_features(latest)

    # ============================
    # SAFETY CHECK (VERY IMPORTANT)
    # ============================

    missing = [f for f in FEATURES if f not in latest.columns]
    if missing:
        raise ValueError(f"Missing features: {missing}")

    # Ensure correct order
    X = latest.reindex(columns=FEATURES)

    # ============================
    # MODEL PREDICTIONS
    # ============================

    cat = cat_model.predict_proba(X)[0][1]
    xgb = xgb_model.predict_proba(X)[0][1]
    lgb = lgbm_model.predict_proba(X)[0][1]

    # ============================
    # ENSEMBLE
    # ============================

    probability = (
        0.40 * cat +
        0.35 * xgb +
        0.25 * lgb
    )

    # Safety clipping
    probability = max(0, min(1, probability))

    confidence = round(probability * 100, 2)

    # ============================
    # FINAL SIGNAL
    # ============================

    if probability > threshold_high:
      signal = "STRONG BUY"
    elif probability > threshold:
      signal = "BUY"
    elif probability < sell_threshold:
      signal = "SELL"
    else:
      signal = "NO TRADE"

    # ============================
    # OUTPUT
    # ============================

    return {
        "signal": signal,
        "confidence": confidence,
        "probability": probability,
        "catboost": float(cat),
        "xgboost": float(xgb),
        "lightgbm": float(lgb),
        "interesting_signal": int(latest.iloc[0]["INTERESTING_SIGNAL"])
    }
