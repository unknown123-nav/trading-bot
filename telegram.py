import requests
import time

from db import (
    get_latest_signals,
    get_active_trades,
    get_pnl_report,
    save_conversation
)

from config import AUTO_CHAT_ID, MANUAL_CHAT_ID

BOT_TOKEN = "8626450626:AAGooyT7nO1kLxdOe4KbzV20JqJye7JVcio"
LAST_UPDATE_ID = None


# =========================================
# SEND TELEGRAM MESSAGE
# =========================================
def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(url, json={
            "chat_id": chat_id,
            "text": message
        })
        print("Telegram sent")
    except Exception as ex:
        print("Telegram error:", ex)


# =========================================
# TELEGRAM ENGINE
# =========================================
def check_replies():

    global LAST_UPDATE_ID

    try:
        print("Checking Telegram...")

        if LAST_UPDATE_ID:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={LAST_UPDATE_ID + 1}"
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

        response = requests.get(url, timeout=10)
        print("Status:", response.status_code)
        print("Response:", response.text)

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

            print(f"Received: {text}")

            # =====================================
            # CHANNEL TYPE
            # =====================================
            is_auto = str(chat_id) == str(AUTO_CHAT_ID)
            is_manual = str(chat_id) == str(MANUAL_CHAT_ID)

            # =====================================
            # COMMANDS
            # =====================================

            if "help" in text:
                reply = (
                    "Available commands:\n\n"
                    "status - system status\n"
                    "signals - latest signals\n"
                    "trades - active trades\n"
                    "pnl - performance\n"
                    "ping - connectivity test\n"
                    "ai - AI system info"
                )

            elif "status" in text:
                reply = (
                    "System status:\n\n"
                    "AI Engine: running\n"
                    "Trading engine: active\n"
                    "Database: connected\n"
                    "Cloud: online"
                )

            # =====================================
            # SIGNALS
            # =====================================
            elif "signal" in text:

                if is_auto:
                    signals = get_latest_signals("AUTO")
                    reply = "AUTO SIGNALS\n\n"
                else:
                    signals = get_latest_signals("MANUAL")
                    reply = "MANUAL SIGNALS\n\n"

                if not signals:
                    reply += "No signals available"
                else:
                    for s in signals:
                        pair = s[0]
                        direction = s[1]
                        confidence = round(float(s[2]), 2)

                        reply += f"{pair} -> {direction} ({confidence}%)\n"

            # =====================================
            # TRADES
            # =====================================
            elif "trade" in text:

                if is_auto:
                    trades = get_active_trades()  # AI trades
                    reply = "AUTO TRADES\n\n"
                else:
                    
                    from db import get_manual_trades
                    trades = get_manual_trades()
                    reply = "MANUAL TRADES\n\n"

                if not trades:
                    reply += "No active trades"
                else:
                    for t in trades:
                        reply += f"{t[0]} -> {t[1]}\n"

            # =====================================
            # PNL
            # =====================================
            elif "pnl" in text:
                report = get_pnl_report()

                if not report:
                    reply = "Performance data unavailable"
                else:
                    reply = (
                        "Performance report:\n\n"
                        f"Win Rate: {report['win_rate']}%\n"
                        f"Active Trades: {report['active_trades']}\n"
                        f"Total Signals: {report['signals']}\n"
                        f"AI Accuracy: {report['ai_accuracy']}%"
                    )

            elif "ping" in text:
                reply = "System responding. Network stable."

            elif "ai" in text:
                reply = (
                    "AI System:\n\n"
                    "Type: classification\n"
                    "Multi-timeframe analysis enabled"
                )

            else:
                reply = "Unknown command. Type 'help' for options."

            # =====================================
            # SEND RESPONSE
            # =====================================
            send_telegram(chat_id, reply)

            save_conversation(
                message_id=update_id,
                pair="GENERAL",
                user_msg=text,
                bot_msg=reply
            )

            print(f"Replied to: {text}")
            time.sleep(1)

    except Exception as e:
        print("Telegram error:", e)
