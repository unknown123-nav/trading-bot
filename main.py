import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import os
import time
import requests
import mysql.connector
from bot_engine import run_bots

# ==============================
#  DUMMY WEB SERVER
# ==============================
def start_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    with TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
        print(f" Dummy server running on port {port}")
        httpd.serve_forever()

threading.Thread(target=start_dummy_server, daemon=True).start()

# ==============================
#  KEEP ALIVE (PREVENT SLEEP)
# ==============================
def keep_alive():
    url = os.environ.get(
        "RENDER_URL",
        "https://trading-bot-1-5457.onrender.com"
    )

    while True:
        try:
            requests.get(url)
            print(" Pinged self to keep alive")
        except Exception as e:
            print("Ping error:", e)

        time.sleep(300)  # every 5 minutes

threading.Thread(target=keep_alive, daemon=True).start()

# ==============================
#  DATABASE CONNECTION FUNCTION
# ==============================
def get_connection():
    return mysql.connector.connect(
        host="hopper.proxy.rlwy.net",
        user="root",
        password="LygrVoBHOocJwSIDejJqBNVIjbziUGxo",
        database="railway",
        port=28847
    )

print(" Connected to Railway DB")
print(" Python Bot Engine Started")


# ==============================
#  CLEANUP FUNCTION 
# ==============================
def clean_old_data():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print(" Cleaning old data...")

        # signals_1m
        cursor.execute("""
            DELETE FROM signals_1m
            WHERE id NOT IN (
                SELECT id FROM (
                    SELECT id FROM signals_1m
                    ORDER BY created_at DESC
                    LIMIT 20000
                ) t
            )
        """)

        # signals_3m
        cursor.execute("""
            DELETE FROM signals_3m
            WHERE id NOT IN (
                SELECT id FROM (
                    SELECT id FROM signals_3m
                    ORDER BY created_at DESC
                    LIMIT 20000
                ) t
            )
        """)

        # signals_30m
        cursor.execute("""
            DELETE FROM signals_30m
            WHERE id NOT IN (
                SELECT id FROM (
                    SELECT id FROM signals_30m
                    ORDER BY created_at DESC
                    LIMIT 20000
                ) t
            )
        """)

        conn.commit()
        conn.close()

        print("Cleanup completed")

    except Exception as e:
        print("Cleanup error:", e)
# ==============================
#  BOT LOOP 
# ==============================

counter = 0

while True:
    try:
        print(" Running bot cycle...")

        run_bots()

        counter += 1

        #  run cleanup every 60 cycles (~1 hour)
        if counter % 60 == 0:
            clean_old_data()

    except Exception as e:
        print("ERROR:", e)

    time.sleep(60)
