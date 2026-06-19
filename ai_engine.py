import os
import joblib
import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

cat_model = joblib.load("catboost_model.pkl")
xgb_model = joblib.load("xgboost_model.pkl")
lgbm_model = joblib.load("lightgbm_model.pkl")

weights = joblib.load("ensemble_model.pkl")
best_threshold = float(joblib.load("best_threshold.pkl"))

CAT_WEIGHT = weights["catboost_weight"]
XGB_WEIGHT = weights["xgboost_weight"]
LGBM_WEIGHT = weights["lightgbm_weight"]

print("ENSEMBLE AI LOADED")

# ==========================================
# ENSEMBLE PREDICTION
# ==========================================
def predict_trade(features):

    cat_prob = cat_model.predict_proba(features)[0][1]
    xgb_prob = xgb_model.predict_proba(features)[0][1]
    lgbm_prob = lgbm_model.predict_proba(features)[0][1]

    ensemble_prob = (
        CAT_WEIGHT * cat_prob
        + XGB_WEIGHT * xgb_prob
        + LGBM_WEIGHT * lgbm_prob
    )

    return ensemble_prob

# ==========================================
# SIGNAL GENERATION
# ==========================================

def predict_signal(df, symbol, timeframe):

    try:

        if len(df) < 30:
            return "DOWN", 0

        latest = df.iloc[0]

        # Trend strength
        sma10 = df["close"].head(10).mean()
        sma30 = df["close"].head(30).mean()

        trend_strength = (
            abs(sma10 - sma30)
            / (sma30 + 1e-8)
        ) * 100

        # Channel position
        upper = df["high"].head(20).max()
        lower = df["low"].head(20).min()

        channel_position = (
            latest["close"] - lower
        ) / (
            upper - lower + 1e-8
        )

        bb_width = (
            latest["BB_UPPER"]
            - latest["BB_LOWER"]
        )

        features = np.array([[
            latest["EMA20"],
            latest["EMA50"],
            latest["RSI"],
            latest["ATR"],
            latest["NATR"],
            latest["BB_WIDTH"],
            latest["CHAIKIN_VOL"],
            latest["VQI"],
            latest["TREND_STRENGTH"],
            latest["CHANNEL_POSITION"]
        ]])

        probability = predict_trade(features)

        # confidence %
        confidence = round(probability * 100, 2)
        confidence = min(confidence, 99)

        # use optimized threshold
        if probability >= best_threshold:
            direction = "UP"
        else:
            direction = "DOWN"

        print(
            f"AI → {symbol} {timeframe}"
            f" | Prob={probability:.4f}"
            f" | Direction={direction}"
            f" | Confidence={confidence}"
        )

        return direction, confidence

    except Exception as e:

        print("AI Signal Error:", e)

        return "DOWN", 0
