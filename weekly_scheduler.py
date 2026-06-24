import subprocess
import time
import datetime

print("WEEKLY SCHEDULER STARTED")

last_run_date = None

while True:

    try:

        now = datetime.datetime.now()

        if (
            now.weekday() == 6
            and now.hour == 0
        ):

            today = now.date()

            if last_run_date != today:

                print(
                    "STARTING WEEKLY RETRAINING"
                )

                subprocess.run(

                    ["python", "weekly_retrainer.py"]

                )

                print(
                    "RETRAINING FINISHED"
                )

                last_run_date = today

        time.sleep(3600)

    except Exception as e:

        print(
            "Scheduler error:",
            e
        )

        time.sleep(300)
