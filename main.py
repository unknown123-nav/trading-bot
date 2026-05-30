import threading
import os
import time
import requests

from flask import Flask

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

    from telegram import check_replies

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

    # ✅ import ONLY when needed (after Flask starts)
    from bot_engine import run_bot, monitor_trades

    while True:
        try:
            print("🔁 Running trading cycle")
            run_bot()
            monitor_trades()
        except Exception as e:
            print("Trading Error:", e)

        time.sleep(300)
# =========================================
# ✅ START THREADS
# =========================================
if __name__ == "__main__":

    # ✅ START FLASK IMMEDIATELY
    def start_flask():
        app.run(
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 10000)),
            debug=False,
            threaded=True
        )

    # ✅ RUN FLASK FIRST (CRITICAL)
    threading.Thread(target=start_flask).start()

    # ✅ DELAY HEAVY STUFF
    time.sleep(3)

    # ✅ THEN START YOUR BOT
    threading.Thread(target=assistant_loop, daemon=True).start()
    threading.Thread(target=trading_loop, daemon=True).start()

    # ✅ KEEP MAIN THREAD ALIVE
    while True:
        time.sleep(60)
