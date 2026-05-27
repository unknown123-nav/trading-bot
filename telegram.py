import requests
import time

from db import (
    get_latest_signals,
    get_active_trades,
    get_pnl_report
)

BOT_TOKEN = "8665738800:AAEPbMqnFY_ZWPWpFfcqmOhZQBLuOHKLA-4"
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

        for update in updates:

            update_id = update["update_id"]

            # ✅ skip old updates safely
            if LAST_UPDATE_ID is not None and update_id <= LAST_UPDATE_ID:
                continue

            LAST_UPDATE_ID = update_id

            message = update.get("message", {})
            if not message:
                continue

            if message.get("from", {}).get("is_bot"):
                continue

            text = message.get("text", "").strip().lower()
            chat_id = message["chat"]["id"]

            if not text:
                continue

            print(f"📩 Received: {text}")

            # ===============================
            # COMMANDS
            # ===============================

            if text == "help":
                reply = "📚 Commands: status, signals, trades, pnl"

            elif text == "status":
                reply = "✅ System running"

            elif text == "signals":
                signals = get_latest_signals()
                if not signals:
                    reply = "⚠️ No signals"
                else:
                    reply = "🚨 Signals:\n\n"
                    for s in signals:
                        reply += f"{s[0]} → {s[1]} ({round(float(s[2]),2)}%)\n"

            elif text == "trades":
                trades = get_active_trades()
                if not trades:
                    reply = "⚠️ No trades"
                else:
                    reply = "📂 Trades:\n\n"
                    for t in trades:
                        reply += f"{t[0]} → {t[1]}\n"

            elif text == "pnl":
                report = get_pnl_report()
                if not report:
                    reply = "⚠️ No report"
                else:
                    reply = f"💰 Win Rate: {report['win_rate']}%"

            else:
                reply = "❌ Unknown command"

            # ✅ SEND MESSAGE
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply}
            )

            print(f"✅ Replied to: {text}")

    except Exception as e:
        print("Telegram error:", e)
