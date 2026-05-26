import threading
import os
import time
import requests
import mysql.connector

from flask import Flask

from bot_engine import (
    run_bots,
    monitor_trades
)

from telegram import check_replies


# =========================================
# FLASK SERVER
# =========================================

app = Flask(__name__)

@app.route("/")
def home():

    return "KRYPTRA AI ENGINE RUNNING"


# =========================================
# DATABASE CONNECTION
# =========================================

def get_connection():

    return mysql.connector.connect(
        host="hopper.proxy.rlwy.net",
        user="root",
        password="LygrVoBHOocJwSIDejJqBNVIjbziUGxo",
        database="railway",
        port=28847
    )


print("✅ Connected to Railway DB")
print("🤖 Python Bot Engine Started")


# =========================================
# CLEANUP FUNCTION
# =========================================

def clean_old_data():

    try:

        conn = get_connection()

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
# ASSISTANT BOT LOOP
# =========================================

def assistant_loop():

    print("🤖 Assistant Bot Started")

    while True:

        try:

            check_replies()

        except Exception as e:

            print("Assistant Bot Error:", e)

        time.sleep(3)


# =========================================
# TRADING LOOP
# =========================================

def trading_loop():

    counter = 0

    while True:

        try:

            print("🚀 Running bot cycle...")

            run_bots()

            monitor_trades()

            counter += 1

            if counter % 60 == 0:

                clean_old_data()

        except Exception as e:

            print("Trading Loop Error:", e)

        time.sleep(60)


# =========================================
# START THREADS
# =========================================

threading.Thread(
    target=assistant_loop,
    daemon=True
).start()

threading.Thread(
    target=trading_loop,
    daemon=True
).start()


# =========================================
# START FLASK APP
# =========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
