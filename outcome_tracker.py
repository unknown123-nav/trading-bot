from db import get_connection

def update_target(pair,timeframe,entry_price,pnl):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        target = 1

        if pnl <= 0:
            target = 0

        cursor.execute("""

        UPDATE ai_training_dataset

        SET target=%s

        WHERE pair=%s
        AND timeframe=%s
        AND price=%s

        ORDER BY id DESC

        LIMIT 1

        """,

        (

        target,
        pair,
        timeframe,
        entry_price

        ))

        conn.commit()

        print("Target updated")

    except Exception as e:

        print("Outcome tracker error:",e)

    finally:

        cursor.close()
        conn.close()
