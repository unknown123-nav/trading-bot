import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import os
import time
from bot_engine import run_bots
import mysql.connector

# ✅ Dummy web server for Render
def start_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    with TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
        print(f"✅ Dummy server running on port {port}")
        httpd.serve_forever()

# ✅ Run dummy server in background
threading.Thread(target=start_dummy_server, daemon=True).start()

# ✅ DB connection
conn = mysql.connector.connect(
    host="hopper.proxy.rlwy.net",
    user="root",
    password="LygrVoBHOocJwSIDejJqBNVIjbziUGxo",
    database="railway",
    port=28847
)

print("✅ Connected to Railway DB")
print("🚀 Python Bot Engine Started")

# ✅ Bot loop
while True:
    try:
        run_bots()
    except Exception as e:
        print("ERROR:", e)

    time.sleep(60)
