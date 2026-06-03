import numpy as np
from tensorflow.keras.models import load_model
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

model = load_model("trading_ai_model_v2.h5")
print(" AI MODEL V2 LOADED")

def predict_trade(pair, timeframe, direction, confidence, delta, percentile, pnl):
    try:
        pair_map = {
            "BTC-GBP": 0,
            "ETH-GBP": 1,
            "SOL-GBP": 2
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

        features = np.array([[ 
            pair_map.get(pair, 0),
            timeframe_map.get(timeframe, 0),
            direction_map.get(direction, 0),
            float(confidence),
            float(delta),
            float(percentile)
        ]])

        prediction = model.predict(features, verbose=0)

        return float(prediction[0][0])

    except Exception as e:
        print("❌ AI Prediction Error:", e)
        return 0.0


# =========================================
# SIGNAL GENERATION 
# =========================================
def predict_signal(df, symbol, timeframe):
    try:
        if len(df) < 2:
            return "DOWN", 0

        last = df.iloc[0]
        prev = df.iloc[1]

        delta = float(last['close']) - float(prev['close'])
        direction = "UP" if delta > 0 else "DOWN"

        percentile = abs(delta) / float(prev['close']) if float(prev['close']) != 0 else 0

        #  AI prediction
        probability = predict_trade(
            pair=symbol,
            timeframe=timeframe,
            direction="LONG" if direction == "UP" else "SHORT",
            confidence=abs(delta),
            delta=delta,
            percentile=percentile,
            pnl=0
        )

        #  NEW CONFIDENCE LOGIC (MUCH BETTER)
        confidence = round(probability * 100, 2)

        #  BOOST strong moves
        if abs(delta) > 0.5:
            confidence += 5

        if abs(delta) > 1.0:
            confidence += 5

        #  HARD LIMIT (SAFE)
        confidence = min(confidence, 99)

        #  DEBUG (IMPORTANT)
        print(f"AI → {symbol} {timeframe} | Prob: {probability:.4f} | Conf: {confidence}")

        return direction, confidence

    except Exception as e:
        print(" AI Signal Error:", e)
        return "DOWN", 0
