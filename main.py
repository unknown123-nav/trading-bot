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
# ✅ DATABASE CONNECTION
# =========================================

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="hopper.proxy.rlwy.net",
            user="root",
            password="LygrVoBHOocJwSIDejJqBNVIjbziUGxo",
            database="railway",
            port=28847
        )
        return conn
    except Exception as e:
        print("DB Connection Error:", e)
        return None


print("✅ Python Bot Engine Starting...")


# =========================================
# ✅ CLEANUP FUNCTION
# =========================================

def clean_old_data():
    try:
        conn = get_connection()

        if not conn:
            return

        cursor = conn.cursor()

        print("🧹 Cleaning old data...")

        tables = [
            "signals_1m",
            "signals_3m",
            "signals_5m",
            "signals_15m",
            "signals_30m",
            "signals_1h"
        ]

        for table in tables:
            cursor.execute(f"""
                DELETE FROM {table}
                WHERE id NOT IN (
                    SELECT id FROM (
                        SELECT id FROM {table}
                        ORDER BY created_at DESC
                        LIMIT 20000
                    ) t
                )
            """)

        conn.commit()
        conn.close()

        print("✅ Cleanup completed")

    except Exception as e:
        print("Cleanup error:", e)


# =========================================
# ✅ KEEP ALIVE (EXTRA SAFETY)
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
# ✅ TELEGRAM ASSISTANT LOOP
# =========================================

def assistant_loop():
    print("🤖 Assistant Bot Started")

    while True:
        try:
            check_replies()
        except Exception as e:
            print("Assistant Error:", e)

        time.sleep(3)


# =========================================
# ✅ TRADING LOOP
# =========================================

def trading_loop():
    print("🚀 Trading Engine Started")

    counter = 0

    while True:
        try:
            print("🔁 Running trading cycle...")

            run_bots()
            monitor_trades()

            counter += 1

            # ✅ Cleanup every ~1 hour
            if counter % 60 == 0:
                clean_old_data()

        except Exception as e:
            print("Trading Loop Error:", e)

        time.sleep(60)


# =========================================
# ✅ START THREADS
# =========================================

threading.Thread(target=assistant_loop, daemon=True).start()
threading.Thread(target=trading_loop, daemon=True).start()


# =========================================
# ✅ START APP (CRITICAL FOR RENDER)
# =========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
