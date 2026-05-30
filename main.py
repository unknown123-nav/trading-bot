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

    try:
        from bot_engine import run_bot, monitor_trades
        print("✅ bot_engine imported")
    except Exception as e:
        print("❌ Import failed:", str(e))
        return

    while True:
        try:
            print("💓 BOT ALIVE")

            run_bot()
            monitor_trades()

        except Exception as e:
            print("❌ Trading Error:", str(e))

        time.sleep(300)

# =========================================
# ✅ START THREADS
# =========================================
# ✅ START FLASK
def start_flask():
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=False,
        threaded=True
    )


# ✅ SAFE THREADS
def safe_trading():
    try:
        trading_loop()
    except Exception as e:
        print("❌ Trading crashed:", e)


def safe_assistant():
    try:
        assistant_loop()
    except Exception as e:
        print("❌ Assistant crashed:", e)

print("✅ MAIN STARTED")

# ✅ START BOT THREADS FIRST
threading.Thread(target=safe_trading).start()
threading.Thread(target=safe_assistant).start()

# ✅ small delay (optional but helpful)
time.sleep(2)

# ✅ FORCE ONE RUN (VERY IMPORTANT)
try:
    from bot_engine import run_bot, monitor_trades
    print("✅ bot_engine imported (main)")

    print("⚡ FIRST RUN FROM MAIN")
    run_bot()
    monitor_trades()

except Exception as e:
    print("❌ First run failed:", e)
# ✅ RUN FLASK IN MAIN THREAD (IMPORTANT)
app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
    debug=False,
    threaded=True
)
