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
    return "Bot running "

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
            print(" Assistant Error:", e)

        time.sleep(2)

def weekly_loop():

    print("WEEKLY RETRAINER STARTED")

    try:

        import weekly_scheduler

    except Exception as e:

        print(
            "Weekly thread error:",
            e
        )
# =========================================
# ✅ TRADING THREAD
# =========================================
def trading_loop():
    print(" Trading Engine Started")

    while True:
        print("Loop running...")
        try:
            print("Importing bot_engine...")
            from bot_engine import run_bot
            print("bot_engine imported")

            print("BOT STARTING...")
            run_bot()

        except Exception as e:
            import traceback
            traceback.print_exc()
            print("Trading crashed:", e)

            # ✅ restart after crash
            time.sleep(5)

# =========================================
# ✅ START THREADS
# =========================================
print("MAIN STARTED")

threading.Thread(target=trading_loop, daemon=True).start()
threading.Thread(target=assistant_loop, daemon=True).start()

threading.Thread(
    target=weekly_loop,
    daemon=True
).start()
# ✅ FLASK RUN
app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
    debug=False
)
