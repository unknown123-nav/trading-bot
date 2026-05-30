import threading
import os
import time
import requests

from flask import Flask
from bot_engine import run_bot, monitor_trades
from telegram import check_replies

# =========================================
# ✅ FLASK (FOR RENDER)
# =========================================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running ✅"


# =========================================
# ✅ TELEGRAM ASSISTANT
# =========================================
def assistant_loop():
    print("🤖 Assistant Started")

    while True:
        try:
            check_replies()
        except Exception as e:
            print("Assistant Error:", e)

        time.sleep(2)


# =========================================
# ✅ TRADING LOOP (SAFE)
# =========================================
def trading_loop():
    print("🚀 Trading Engine Started")

    while True:
        try:
            print("🔁 Running trading cycle")

            run_bot()
            monitor_trades()

        except Exception as e:
            print("Trading Error:", e)

        time.sleep(300)   # ✅ every 5 minutes


# =========================================
# ✅ START THREADS
# =========================================
if __name__ == "__main__":

    threading.Thread(target=assistant_loop, daemon=True).start()
    threading.Thread(target=trading_loop, daemon=True).start()

    # ✅ ONLY ONE RUN (IMPORTANT)
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
