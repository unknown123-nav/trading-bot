import numpy as np
from tensorflow.keras.models import load_model

# =========================================
# ✅ LOAD MODEL
# =========================================
model = load_model("trading_ai_model.h5")
print("🧠 AI MODEL LOADED")


# =========================================
# ✅ CORE PREDICT FUNCTION
# =========================================
def predict_trade(pair, timeframe, direction, confidence, delta, percentile, pnl):
    try:

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
            "1H": 5
        }

        direction_map = {
            "LONG": 0,
            "SHORT": 1
        }

        pair_encoded = pair_map.get(pair, 0)
        timeframe_encoded = timeframe_map.get(timeframe, 0)
        direction_encoded = direction_map.get(direction, 0)

        features = np.array([[
            pair_encoded,
            timeframe_encoded,
            direction_encoded,
            float(confidence),
            float(delta),
            float(percentile),
            float(pnl)
        ]])

        prediction = model.predict(features, verbose=0)
        probability = float(prediction[0][0])

        return probability

    except Exception as e:
        print("AI Prediction Error:", e)
        return 0.0


# =========================================
# ✅ SIGNAL FUNCTION
# =========================================
def predict_signal(df, symbol, timeframe):
    try:

        if len(df) < 2:
            return "DOWN", 0

        last = df.iloc[0]
        prev = df.iloc[1]

        delta = float(last['close']) - float(prev['close'])

        direction = "UP" if delta > 0 else "DOWN"

        confidence_input = abs(delta)

        if prev['close'] != 0:
            percentile = abs(delta) / float(prev['close'])
        else:
            percentile = 0

        probability = predict_trade(
            pair=symbol,
            timeframe=timeframe,
            direction="LONG" if direction == "UP" else "SHORT",
            confidence=confidence_input,
            delta=delta,
            percentile=percentile,
            pnl=0
        )

        confidence = int(max(0, min(probability * 100, 100)))

        return direction, confidence

    except Exception as e:
        print("AI Signal Error:", e)
        return "DOWN", 0
