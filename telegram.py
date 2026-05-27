import requests
import time

from db import (
    get_latest_signals,
    get_active_trades,
    get_pnl_report
)

BOT_TOKEN = "PUT_YOUR_TOKEN_HERE"
CHAT_ID = "-5211298112"

LAST_UPDATE_ID = None


# =========================================
# ✅ SEND TELEGRAM MESSAGE
# =========================================
def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, json=payload)
        print("✅ Telegram sent:", response.text)
    except Exception as ex:
        print("Telegram error:", ex)


# =========================================
# ✅ TELEGRAM REPLY ENGINE (FIXED ✅)
# =========================================
def check_replies():

    global LAST_UPDATE_ID

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

        response = requests.get(url, timeout=10)
        data = response.json()

        if not data.get("ok"):
            return

        updates = data.get("result", [])

        if not updates:
            return

        # ✅ ONLY PROCESS LATEST MESSAGE (KEY FIX 🔥)
        latest_update = updates[-1]
        update_id = latest_update["update_id"]

        # ✅ IGNORE OLD UPDATES
        if LAST_UPDATE_ID is not None and update_id <= LAST_UPDATE_ID:
            return

        LAST_UPDATE_ID = update_id

        message = latest_update.get("message", {})

        if not message:
            return

        if message.get("from", {}).get("is_bot"):
            return

        text = message.get("text", "").strip().lower()
        chat_id = message["chat"]["id"]

        if not text:
            return

        print(f"📩 Received: {text}")

        # =====================================
        # ✅ COMMAND HANDLING
        # =====================================

        if text == "status":
            reply = "🟢 KRYPTRA AI STATUS: ONLINE ✅"

        elif text == "help":
            reply = (
                "📚 Commands:\n\n"
                "status\nsignals\ntrades\npnl\nping\nhelp"
            )

        elif text == "ping":
            reply = "🏓 Pong! System is responsive ✅"

        elif text == "signals":
            signals = get_latest_signals()

            if not signals:
                reply = "⚠️ No signals available"
            else:
                reply = "🚨 SIGNALS:\n\n"
                for s in signals:
                    reply += f"{s[0]} → {s[1]} ({round(float(s[2]), 2)}%)\n"

        elif text == "trades":
            trades = get_active_trades()

            if not trades:
                reply = "⚠️ No active trades"
            else:
                reply = "📂 ACTIVE TRADES:\n\n"
                for t in trades:
                    reply += f"{t[0]} → {t[1]}\n"

        elif text == "pnl":
            report = get_pnl_report()

            if not report:
                reply = "⚠️ No report available"
            else:
                reply = (
                    f"💰 Win Rate: {report['win_rate']}%\n"
                    f"📊 Active Trades: {report['active_trades']}\n"
                    f"⚡ Signals: {report['signals']}\n"
                    f"🟢 Accuracy: {report['ai_accuracy']}%"
                )

        else:
            reply = "❌ Unknown command — type 'help'"

        # ✅ SEND RESPONSE
        send_telegram(chat_id, reply)

        print(f"✅ Replied to: {text}")

    except Exception as e:
        print("🚨 Telegram error:", e)
