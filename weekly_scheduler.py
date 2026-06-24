import time
import datetime
from weekly_retrainer import *

print("WEEKLY SCHEDULER STARTED")

last_run_date = None

while True:

    try:

        now = datetime.datetime.now()

        # Sunday = 6
        if (
            now.weekday() == 6
            and now.hour == 0
        ):

            today = now.date()

            if last_run_date != today:

                print(
                    "STARTING WEEKLY RETRAINING..."
                )

                try:

                    import weekly_retrainer

                    print(
                        "RETRAINING COMPLETE"
                    )

                except Exception as e:

                    print(
                        "Retraining error:",
                        e
                    )

                last_run_date = today

        time.sleep(
            3600
        )

    except Exception as e:

        print(
            "Scheduler error:",
            e
        )

        time.sleep(
            300
        )
