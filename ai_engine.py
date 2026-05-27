import numpy as np

from tensorflow.keras.models import load_model

# =========================================
# LOAD MODEL
# =========================================

model = load_model(
    "trading_ai_model.h5"
)

print("🧠 AI MODEL LOADED")

# =========================================
# PREDICT CONTINUATION
# =========================================

def predict_trade(
    pair,
    timeframe,
    direction,
    confidence,
    delta,
    percentile,
    pnl
):

    try:

        # =====================================
        # ENCODE VALUES
        # =====================================

        pair_map = {
            "BTC-USDT": 0,
            "ETH-USDT": 1,
            "SOL-USDT": 2,
            "XRP-USDT": 3,
            "ADA-USDT": 4,
            "DOGE-USDT": 5
        }

        timeframe_map = {
            "1m": 0,
            "3m": 1,
            "5m": 2,
            "15m": 3,
            "30m": 4,
            "1h": 5
        }

        direction_map = {
            "LONG": 0,
            "SHORT": 1
        }

        # =====================================
        # CONVERT
        # =====================================

        pair_encoded = pair_map.get(pair, 0)

        timeframe_encoded = timeframe_map.get(timeframe, 0)

        direction_encoded = direction_map.get(direction, 0)

        # =====================================
        # CREATE FEATURES
        # =====================================

        features = np.array([
            [
                pair_encoded,
                timeframe_encoded,
                direction_encoded,
                confidence,
                delta,
                percentile,
                pnl
            ]
        ])

        # =====================================
        # PREDICT
        # =====================================

        print("Running AI prediction...")
        prediction = model.predict(
            features,
            verbose=0
        )

        probability = float(
            prediction[0][0]
        )

        return probability
        print(f"AI Probability: {probability}")

    except Exception as e:

        print("AI Prediction Error:", e)

        return 0
