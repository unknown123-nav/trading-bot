from telegram import check_replies
import telegram
import time

# =====================================
# ASSISTANT BOT TOKEN
# =====================================

telegram.BOT_TOKEN = "8626450626:AAExgPikQRBaL3HnE98v58ZrmsqjrfWr99c"

print("🤖 Assistant Bot Started")

while True:

    try:

        check_replies()

    except Exception as e:

        print("Assistant Bot Error:", e)

    time.sleep(3)
