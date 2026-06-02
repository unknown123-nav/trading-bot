import threading
import os
import time

from flask import Flask

# =========================================
# ✅ FLASK
# =========================================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running ✅"

# =========================================
# ✅ TELEGRAM ASSISTANT (SAFE LOOP)
# =========================================
def assistant_loop():
    print("🤖 Assistant Started")

    while True:
        try:
            from telegram import check_replies
            check_replies()
        except Exception as e:
            print("❌ Assistant Error:", e)

        time.sleep(2)

# =========================================
# ✅ TRADING THREAD
# =========================================
def trading_loop():
    print("🚀 Trading Engine Started")

    while True:
        try:
            from bot_engine import run_bot
            print("✅ bot_engine imported")

            print("💓 BOT STARTING...")
            run_bot()

        except Exception as e:
            print("❌ Trading crashed:", e)

            # ✅ restart after crash
            time.sleep(5)

# =========================================
# ✅ START THREADS
# =========================================
print("✅ MAIN STARTED")

threading.Thread(target=trading_loop, daemon=True).start()
threading.Thread(target=assistant_loop, daemon=True).start()

# ✅ FLASK RUN
app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
    debug=False
)
