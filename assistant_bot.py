from telegram import check_replies
import telegram
import time

# =====================================
# ASSISTANT BOT TOKEN
# =====================================

telegram.BOT_TOKEN = "8625282562:AAGNQZgdVK0mPYrXJ2GOAlc55HW74_5glak"

print("🤖 Assistant Bot Started")

while True:

    try:

        check_replies()

    except Exception as e:

        print("Assistant Bot Error:", e)

    time.sleep(3)
