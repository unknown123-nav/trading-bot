from flask import Flask, request, jsonify

import numpy as np
import os

from tensorflow.keras.models import load_model

# =========================
# LOAD MODEL
# =========================

model = load_model(
        "trading_ai_model.h5"
    )

# =========================
# CREATE API
# =========================

app = Flask(__name__)

# =========================
# PREDICT
# =========================

@app.route('/predict', methods=['POST'])
def predict():

    data = request.json

    features = np.array([
        [
            data["Pair"],
            data["Timeframe"],
            data["Direction"],
            data["Confidence"],
            data["Delta"],
            data["Percentile"],
            data["PNL"]
        ]
    ])

    prediction = model.predict(features)

    probability = float(prediction[0][0])

    return jsonify({
        "continuation_probability":
            probability
    })

# =========================
# RUN SERVER
# =========================

if __name__ == '__main__':

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host='0.0.0.0',
        port=port
    )
