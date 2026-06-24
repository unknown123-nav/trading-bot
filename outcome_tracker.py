import mysql.connector
from datetime import datetime
from config import DB_CONFIG
from market import get_data


def update_targets():

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:

        cursor.execute("""

        SELECT
        id,
        pair,
        timeframe,
        price,
        direction,
        time

        FROM ai_training_dataset

        WHERE target IS NULL

        """)

        rows = cursor.fetchall()

        for row in rows:

            signal_id = row[0]
            pair = row[1]
            timeframe = row[2]
            entry_price = float(row[3])
            direction = row[4]
            signal_time = row[5]

            elapsed_hours = (
                datetime.now() - signal_time
            ).total_seconds()/3600

            # wait enough candles

            if timeframe == "30m" and elapsed_hours < 2:
                continue

            if timeframe == "1H" and elapsed_hours < 4:
                continue

            df = get_data(pair, timeframe, 1)

            if df.empty:
                continue

            current_price = float(
                df.iloc[0]["close"]
            )

            target = 0

            if direction == "UP":

                if current_price > entry_price:
                    target = 1

            elif direction == "DOWN":

                if current_price < entry_price:
                    target = 1

            cursor.execute(
                """
                UPDATE ai_training_dataset

                SET target=%s

                WHERE id=%s
                """,
                (
                    target,
                    signal_id
                )
            )

            print(
                f"TARGET UPDATED → {pair} {timeframe} = {target}"
            )

        conn.commit()

    except Exception as e:

        print(
            "Outcome tracker error:",
            e
        )

    finally:

        cursor.close()
        conn.close()
