import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import os
import time
import requests
from bot_engine import run_bots
import mysql.connector

# ==============================
#  DUMMY WEB SERVER (REQUIRED)
# ==============================
def start_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    with TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
        print(f" Dummy server running on port {port}")
        httpd.serve_forever()

threading.Thread(target=start_dummy_server, daemon=True).start()


# ==============================
#  KEEP ALIVE (IMPORTANT )
# ==============================
def keep_alive():
    url = os.environ.get(
        "RENDER_URL",
        "https://trading-bot-1-5457.onrender.com"  #  replace if your URL differs
    )

    while True:
        try:
            requests.get(url)
            print(" Pinged self to keep alive")
        except Exception as e:
            print("Ping error:", e)

        time.sleep(300)  # every 5 min

threading.Thread(target=keep_alive, daemon=True).start()


# ==============================
#  DATABASE CONNECTION
# ==============================
conn = mysql.connector.connect(
    host="hopper.proxy.rlwy.net",
    user="root",
    password="LygrVoBHOocJwSIDejJqBNVIjbziUGxo",
    database="railway",
    port=28847
)

print(" Connected to Railway DB")
print(" Python Bot Engine Started")


# ==============================
#  BOT LOOP
# ==============================
while True:
    try:
        print(" Running bot cycle...")
        run_bots()
    except Exception as e:
        print("ERROR:", e)

    time.sleep(60)
