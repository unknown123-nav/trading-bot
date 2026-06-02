from telegram import check_replies
import telegram
import time

# =====================================
# ASSISTANT BOT TOKEN
# =====================================

telegram.BOT_TOKEN = "8780022222:AAEyVNVseCqJ--tjwNv5nvcbxl4goeFQgC8"

print("🤖 Assistant Bot Started")

while True:

    try:

        check_replies()

    except Exception as e:

        print("Assistant Bot Error:", e)

    time.sleep(3)
