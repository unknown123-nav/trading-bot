import requests
import time


BOT_TOKEN = "7982865948:AAGqCmaBVvptrmbYI-MRSusJC8ZdIIq3_rc"

CHAT_ID = "-5211298112"

LAST_UPDATE_ID = None


# =========================================
# SEND TELEGRAM MESSAGE
# =========================================

def send_telegram(message):

    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
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

        for update in data["result"]:

            update_id = update["update_id"]

            if LAST_UPDATE_ID == update_id:
                continue

            LAST_UPDATE_ID = update_id

            if "message" not in update:
                continue

            message = update["message"]

            text = message.get("text", "")

            chat_id = message["chat"]["id"]

            lower = text.lower()

            reply = None

            # =================================
            # COMMANDS
            # =================================

            if lower == "status":

                reply = (
                    "🤖 Krypta AI Bot Online\n"
                    "✅ Cloud Running\n"
                    "✅ Signals Active\n"
                    "✅ Telegram Connected"
                )

            elif lower == "help":

                reply = (
                    "📚 Commands:\n\n"
                    "status\n"
                    "help\n"
                    "ping"
                )

            elif lower == "ping":

                reply = "🏓 Pong"

            # =================================
            # SEND REPLY
            # =================================

            if reply:

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
