import threading
import os
import time
import requests
import mysql.connector

from flask import Flask

from bot_engine import run_bots, monitor_trades
from telegram import check_replies

# =========================================
# ✅ FLASK SERVER (PREVENT SLEEP)
# =========================================

app = Flask(__name__)

@app.route("/")
def home():
    return "KRYPTRA AI ENGINE RUNNING ✅"


# =========================================
# ✅ KEEP ALIVE
# =========================================

def keep_alive():
    url = os.environ.get(
        "RENDER_URL",
        "https://trading-bot-1-5457.onrender.com"
    )

    while True:
        try:
            requests.get(url)
            print("✅ Self-ping sent")
        except Exception as e:
            print("Ping error:", e)

        time.sleep(300)


threading.Thread(target=keep_alive, daemon=True).start()

# =========================================
# ✅ TELEGRAM ASSISTANT LOOP (IMPORTANT)
# =========================================

def assistant_loop():
    print("🤖 Assistant Bot Started")

    while True:
        try:
            check_replies()
        except Exception as e:
            print("Assistant Error:", e)

        # ✅ keep fast response
        time.sleep(1)

# =========================================
# ✅ TRADING LOOP (SAFE VERSION)
# =========================================

def trading_loop():
    print("🚀 Trading Engine Started")

    counter = 0

    while True:
        try:
            print("🔁 Running trading cycle...")

            # ✅ RUN ONCE (NO MULTIPLE THREADS)
            run_bots()

            counter += 1

            if counter % 6 == 0:
                monitor_trades()

        except Exception as e:
            print("Trading Loop Error:", e)

        # ✅ IMPORTANT → slow down system
        time.sleep(90)

# =========================================
# ✅ START THREADS
# =========================================

threading.Thread(target=assistant_loop, daemon=True).start()

threading.Thread(target=trading_loop, daemon=True).start()

# =========================================
# ✅ START APP
# =========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
