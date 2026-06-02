import threading
import os
import time

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
# ✅ TRADING THREAD (FIXED)
# =========================================
def trading_loop():
    print("🚀 Trading Engine Started")

    try:
        from bot_engine import run_bot
        print("✅ bot_engine imported")
    except Exception as e:
        print("❌ Import failed:", str(e))
        return

    try:
        print("💓 BOT STARTING...")
        run_bot()   # ✅ ONLY ONCE (it already loops)
    except Exception as e:
        print("❌ Trading crashed:", e)


# =========================================
# ✅ SAFE THREAD WRAPPERS
# =========================================
def safe_trading():
    trading_loop()

def safe_assistant():
    assistant_loop()


print("✅ MAIN STARTED")

# ✅ START THREADS
threading.Thread(target=safe_trading, daemon=True).start()
threading.Thread(target=safe_assistant, daemon=True).start()

# ✅ SMALL DELAY
time.sleep(2)

# ✅ RUN FLASK ONLY ONCE (MAIN THREAD)
app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
    debug=False
)
