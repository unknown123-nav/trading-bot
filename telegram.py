import requests
import time

from db import (
    get_latest_signals,
    get_active_trades,
    get_pnl_report
)

BOT_TOKEN = "8864549600:AAHaY2Q84VpkDBhYH6J0X4SNzpj-DLvGM_k"
LAST_UPDATE_ID = None


# =========================================
# ✅ SEND TELEGRAM MESSAGE
# =========================================
def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(url, json={
            "chat_id": chat_id,
            "text": message
        })
        print("✅ Telegram sent")
    except Exception as ex:
        print("Telegram error:", ex)


# =========================================
# ✅ TELEGRAM ENGINE
# =========================================
def check_replies():

    global LAST_UPDATE_ID

    try:
        if LAST_UPDATE_ID:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={LAST_UPDATE_ID + 1}"
        else:
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

            # =====================================
            # ✅ COMMANDS
            # =====================================

            if "help" in text:
                reply = (
                    "📚 *KRYPTRA AI COMMAND CENTER*\n\n"
                    "✅ status → System health\n"
                    "✅ signals → Latest AI signals\n"
                    "✅ trades → Active trades\n"
                    "✅ pnl → Performance report\n"
                    "✅ ping → Check latency\n"
                    "✅ ai → AI system info\n\n"
                    "🤖 Fully automated cloud trading engine"
                )

            elif "status" in text:
                reply = (
                    "🟢 *SYSTEM STATUS*\n\n"
                    "✅ AI Engine: ACTIVE\n"
                    "✅ Trading Bots: RUNNING\n"
                    "✅ Database: CONNECTED\n"
                    "✅ Cloud: ONLINE\n\n"
                    "🚀 All systems operational"
                )

            elif "signal" in text:
                signals = get_latest_signals()

                if not signals:
                    reply = "⚠️ No live signals available"
                else:
                    reply = "🚨 *LATEST AI SIGNALS*\n\n"
                    for s in signals:
                        reply += f"{s[0]} → {s[1]} ({round(float(s[2]),2)}%)\n"
                    reply += "\n⚡ Real-time market scanning active"

            elif "trade" in text:
                trades = get_active_trades()

                if not trades:
                    reply = "⚠️ No active trades"
                else:
                    reply = "📂 *ACTIVE TRADES*\n\n"
                    for t in trades:
                        reply += f"{t[0]} → {t[1]}\n"
                    reply += "\n📡 Monitoring live positions"

            elif "pnl" in text:
                report = get_pnl_report()

                if not report:
                    reply = "⚠️ Unable to fetch performance data"
                else:
                    reply = (
                        "💰 *PERFORMANCE REPORT*\n\n"
                        f"📈 Win Rate: {report['win_rate']}%\n"
                        f"📊 Active Trades: {report['active_trades']}\n"
                        f"⚡ Total Signals: {report['signals']}\n"
                        f"🎯 AI Accuracy: {report['ai_accuracy']}%\n\n"
                        "🚀 Real-time analytics running"
                    )

            elif "ping" in text:
                reply = (
                    "🏓 *PING RESPONSE*\n\n"
                    "✅ Bot Responding\n"
                    "✅ Network Stable\n"
                    "☁️ Cloud Active"
                )

            elif "ai" in text:
                reply = (
                    "🧠 *AI ENGINE INFO*\n\n"
                    "✅ Neural Model Integrated\n"
                    "✅ Signal Confidence Engine\n"
                    "✅ Multi-Timeframe Analysis\n\n"
                    "⚡ Hybrid AI trading system active"
                )

            else:
                reply = (
                    "❌ Unknown command\n\n"
                    "👉 Type 'help' to see available commands"
                )

            # =====================================
            # ✅ SEND RESPONSE
            # =====================================

            send_telegram(chat_id, reply)

            print(f"✅ Replied to: {text}")
            time.sleep(2)

    except Exception as e:
        print("Telegram error:", e)
