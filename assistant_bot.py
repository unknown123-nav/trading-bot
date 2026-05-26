from telegram import check_replies
import telegram
import time

# =====================================
# ASSISTANT BOT TOKEN
# =====================================

telegram.BOT_TOKEN = "8729441908:AAHBGsn2nKoKtvXisGfbhYoM0H9RCNkdhDI"

print("🤖 Assistant Bot Started")

while True:

    try:

        check_replies()

    except Exception as e:

        print("Assistant Bot Error:", e)

    time.sleep(3)
