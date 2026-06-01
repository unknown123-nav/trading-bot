import numpy as np
from tensorflow.keras.models import load_model

# =========================================
# ✅ LOAD MODEL
# =========================================
model = load_model("trading_ai_model.h5")
print(" AI MODEL LOADED")


# =========================================
# ✅ PREDICT CORE (MODEL)
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

        # ✅ ENCODING MAPS
        pair_map = {
            "BTC-USDT": 0,
            "ETH-USDT": 1,
            "SOL-USDT": 2
        }

        timeframe_map = {
            "1m": 0,
            "3m": 1,
            "5m": 2,
            "15m": 3,
            "30m": 4,
            "1H": 5  # 
        }

       direction_map = {
           "LONG": 0,
           "SHORT": 1
       }

        # ✅ ENCODE
        pair_encoded = pair_map.get(pair, 0)
        timeframe_encoded = timeframe_map.get(timeframe, 0)
        direction_encoded = direction_map.get(direction, 0)

        # ✅ FEATURE VECTOR
        features = np.array([[
            pair_encoded,
            timeframe_encoded,
            direction_encoded,
            float(confidence),
            float(delta),
            float(percentile),
            float(pnl)
        ]])

        # ✅ PREDICT
        prediction = model.predict(features, verbose=0)
        probability = float(prediction[0][0])

        return probability

    except Exception as e:
        print("AI Prediction Error:", e)
        return 0.0


# =========================================
# ✅ SIGNAL GENERATOR (USED BY BOT)
# =========================================
def predict_signal(df, symbol, timeframe):
    try:

        if len(df) < 2:
            return "DOWN", 0

        last = df.iloc[0]
        prev = df.iloc[1]

        # ✅ PRICE CHANGE
        delta = float(last['close']) - float(prev['close'])

        # ✅ DIRECTION
        direction = "UP" if delta > 0 else "DOWN"

        # ✅ FEATURES
        confidence_input = abs(delta)
        percentile = abs(delta) / float(prev['close']) if prev['close'] != 0 else 0

        # ✅ MODEL CALL (FIXED ✅)
        probability = predict_trade(
            pair=symbol,  # ✅ FIXED
            timeframe=timeframe,
            direction="LONG" if direction == "UP" else "SHORT",
            confidence=confidence_input,
            delta=delta,
            percentile=percentile,
            pnl=0
        )

        # ✅ CONVERT TO %
        confidence = int(max(0, min(probability * 100, 100)))

        return direction, confidence

    except Exception as e:
        print("AI Signal Error:", e)
        return "DOWN", 0
