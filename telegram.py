import requests


BOT_TOKEN = "7982865948:AAGqCmaBVvptrmbYI-MRSusJC8ZdIIq3_rc"

CHAT_ID = "-5211298112"


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
