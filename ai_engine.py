import numpy as np
from tensorflow.keras.models import load_model
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# LOAD MODEL
model = load_model("trading_ai_model.h5")
print("AI MODEL LOADED")


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
        return float(prediction[0][0])

    except Exception as e:
        print("AI Prediction Error:", e)
        return 0.0

def predict_signal(df, symbol, timeframe):
    try:
        if len(df) < 2:
            return "DOWN", 0

        last = df.iloc[0]
        prev = df.iloc[1]

        delta = float(last['close']) - float(prev['close'])
        direction = "UP" if delta > 0 else "DOWN"

        confidence_input = abs(delta)

        percentile = abs(delta) / float(prev['close']) if float(prev['close']) != 0 else 0

        # ✅ GET AI PROBABILITY FIRST
        probability = predict_trade(
            pair=symbol,
            timeframe=timeframe,
            direction="LONG" if direction == "UP" else "SHORT",
            confidence=confidence_input,
            delta=delta,
            percentile=percentile,
            pnl=0
        )

        # ✅ BASE CONFIDENCE
        confidence = 50 + (probability * 45)
        if abs(delta) > 0.5:
            confidence += 5

        confidence = min(confidence, 95)
        confidence = round(confidence, 2)

        # ✅ BOOST FOR STRONG MOVE
        if abs(delta) > 0.5:
            confidence += 5

        # ✅ LIMIT RANGE
        confidence = min(confidence, 95)
        confidence = round(confidence, 2)

        # ✅ DEBUG LOG
        print(f"AI → {symbol} {timeframe} | Prob: {probability:.4f} | Conf: {confidence}")

        return direction, confidence

    except Exception as e:
        print("AI Signal Error:", e)
        return "DOWN", 0
