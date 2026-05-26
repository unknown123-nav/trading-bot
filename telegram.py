import requests
import time
from db import get_latest_signals
from db import get_active_trades


BOT_TOKEN = "8864549600:AAH8S3USLHU6mOHSbcfxsMdrjYn47TXGCBY"

CHAT_ID = "-5211298112"

LAST_UPDATE_ID = None


# =========================================
# SEND TELEGRAM MESSAGE
# =========================================

def send_telegram(message):

    url = (
    f"https://api.telegram.org/bot"
    f"{BOT_TOKEN}/getUpdates?offset={LAST_UPDATE_ID + 1 if LAST_UPDATE_ID else ''}"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:

        response = requests.post(
            url,
            json=payload
        )

        print(
            "Telegram sent:",
            response.text
        )

    except Exception as ex:

        print(
            "Telegram error:",
            ex
        )


# =========================================
# TELEGRAM REPLY ENGINE
# =========================================

def check_replies():

    global LAST_UPDATE_ID

    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/getUpdates"
    )

    try:

        response = requests.get(url)

        data = response.json()

        if not data["ok"]:
            return

        updates = data["result"]

        # =====================================
        # IGNORE OLD MESSAGES
        # =====================================

        if LAST_UPDATE_ID is None and len(updates) > 0:

            LAST_UPDATE_ID = updates[-1]["update_id"]

            return

        # =====================================
        # PROCESS NEW MESSAGES
        # =====================================

        for update in updates:

            update_id = update["update_id"]

            if update_id <= LAST_UPDATE_ID:
                continue

            LAST_UPDATE_ID = update_id

            if "message" not in update:
                continue

            message = update["message"]
            if message.get("from", {}).get("is_bot"):
                continue

            text = message.get("text", "")

            chat_id = message["chat"]["id"]

            lower = text.lower().strip()

            reply = None

            # =====================================
            # STATUS
            # =====================================

            if lower == "status":

                reply = (
                    "🟢 KRYPTRA AI STATUS\n\n"

                    "🤖 AI Engine: ONLINE\n"
                    "📡 Signal Scanner: ACTIVE\n"
                    "⚡ Trading Engine: RUNNING\n"
                    "☁ Cloud Worker: LIVE\n"
                    "📲 Telegram System: CONNECTED\n\n"

                    "✅ All systems operational."
                )

            # =====================================
            # HELP
            # =====================================

            elif lower == "help":

                reply = (
                    "📚 KRYPTRA AI COMMAND CENTER\n\n"

                    "📌 status → AI system status\n"
                    "📌 signals → latest signals\n"
                    "📌 ai → AI analytics\n"
                    "📌 pnl → performance report\n"
                    "📌 trades → active trades\n"
                    "📌 ping → latency test\n"
                    "📌 help → command list\n\n"

                    "🤖 Autonomous AI trading system active."
                )

            # =====================================
            # PING
            # =====================================

            elif lower == "ping":

                reply = (
                    "🏓 KRYPTRA AI RESPONSE\n\n"

                    "⚡ Connection Stable\n"
                    "☁ Cloud Worker Online\n"
                    "📡 Response Time Normal"
                )

            # =====================================
            # SIGNALS
            # =====================================

            elif lower == "signals":

    signals = get_latest_signals()

    if len(signals) == 0:

        reply = (
            "⚠️ No live signals available."
        )

    else:

        reply = "🚨 LIVE AI SIGNALS\n\n"

        for s in signals:

            reply += (
                f"{s[0]} → "
                f"{s[1]} "
                f"({round(float(s[2]), 2)}%)\n"
            )

        reply += (
            "\n⚡ Real-time market analysis active."
        )

            # =====================================
            # AI
            # =====================================

            elif lower == "ai":

                reply = (
                    "🧠 AI ANALYTICS ENGINE\n\n"

                    "📊 Dataset Status: ACTIVE\n"
                    "📈 Momentum Scanner: RUNNING\n"
                    "⚡ Volatility Detection: ENABLED\n"
                    "🎯 Confidence Engine: ONLINE\n\n"

                    "🤖 Neural trading systems operational."
                )

            # =====================================
            # PNL
            # =====================================

            elif lower == "pnl":

    report = get_pnl_report()

    if report is None:

        reply = (
            "⚠️ Unable to load performance report."
        )

    else:

        reply = (
            "💰 PERFORMANCE REPORT\n\n"

            f"📈 Win Rate: "
            f"{report['win_rate']}%\n"

            f"📊 Active Trades: "
            f"{report['active_trades']}\n"

            f"⚡ Total Signals: "
            f"{report['signals']}\n"

            f"🟢 AI Accuracy: "
            f"{report['ai_accuracy']}%\n\n"

            "🚀 Real-time trading analytics active."
        )

            # =====================================
            # TRADES
            # =====================================

            elif lower == "trades":

    trades = get_active_trades()

    if len(trades) == 0:

        reply = (
            "⚠️ No active trades."
        )

    else:

        reply = "📂 ACTIVE TRADES\n\n"

        for t in trades:

            reply += (
                f"{t[0]} → "
                f"{t[1]}\n"
            )

        reply += (
            "\n⚡ Trade monitoring active."
        )

            # =====================================
            # UNKNOWN COMMAND
            # =====================================

            else:

                reply = (
                    "❌ Unknown Command\n\n"

                    "Type:\n"
                    "help\n\n"

                    "to view available commands."
                )

            # =====================================
            # SEND REPLY
            # =====================================

            send_url = (
                f"https://api.telegram.org/bot"
                f"{BOT_TOKEN}/sendMessage"
            )

            payload = {
                "chat_id": chat_id,
                "text": reply
            }

            requests.post(
                send_url,
                json=payload
            )

            print(
                f"Replied to: {text}"
            )

    except Exception as ex:

        print(
            "Reply engine error:",
            ex
        )
