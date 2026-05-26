import mysql.connector
from config import DB_CONFIG

conn = mysql.connector.connect(**DB_CONFIG)

cursor = conn.cursor()


def save_signal(table, pair, signal_type, confidence, price):

    try:

        query = f"""
        INSERT INTO {table}
        (pair_name, signal_type, confidence, entry_price, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        """

        cursor.execute(query, (
            pair,
            signal_type,
            confidence,
            price
        ))

        conn.commit()

    except Exception as e:
        print("Signal save error:", e)


def update_bot(bot_name, status, pair, pnl):

    try:

        query = """
        INSERT INTO bot_status
        (bot_name, status, current_pair, pnl_today, last_heartbeat)
        VALUES (%s, %s, %s, %s, NOW())

        ON DUPLICATE KEY UPDATE
        status = VALUES(status),
        current_pair = VALUES(current_pair),
        pnl_today = VALUES(pnl_today),
        last_heartbeat = NOW()
        """

        cursor.execute(query, (
            bot_name,
            status,
            pair,
            pnl
        ))

        conn.commit()

    except Exception as e:
        print("Bot update error:", e)



def create_paper_trade(pair, side, entry_price, confidence, timeframe):

    try:

        query = """
        INSERT INTO paper_trades
        (pair, side, entry_price, quantity, leverage, timeframe, ai_confidence, trade_source, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """

        cursor.execute(query, (
            pair,
            side,
            entry_price,
            1,                 # quantity
            1,                 # leverage
            timeframe,
            confidence,
            "AI",
            "OPEN"
        ))

        conn.commit()

        print(f" Trade created: {pair} {side}")

    except Exception as e:
        print("Trade creation error:", e)

def get_latest_signals():

    try:

        query = """
        SELECT pair_name, signal_type, confidence
        FROM signals_1m
        ORDER BY created_at DESC
        LIMIT 5
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        return rows

    except Exception as e:

        print("Signal fetch error:", e)

        return []


def get_active_trades():

    try:

        query = """
        SELECT pair, side
        FROM paper_trades
        WHERE status = 'OPEN'
        ORDER BY created_at DESC
        LIMIT 5
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        return rows

    except Exception as e:

        print("Trade fetch error:", e)

        return []
def get_pnl_report():

    try:

        report = {}

        # =====================================
        # TOTAL SIGNALS
        # =====================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM signals_1m
        """)

        report["signals"] = cursor.fetchone()[0]

        # =====================================
        # ACTIVE TRADES
        # =====================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM paper_trades
            WHERE status = 'OPEN'
        """)

        report["active_trades"] = cursor.fetchone()[0]

        # =====================================
        # WIN RATE
        # =====================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM paper_trades
            WHERE pnl_percent > 0
        """)

        wins = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM paper_trades
            WHERE pnl_percent IS NOT NULL
        """)

        total = cursor.fetchone()[0]

        if total > 0:

            report["win_rate"] = round(
                (wins / total) * 100,
                2
            )

        else:

            report["win_rate"] = 0

        # =====================================
        # AI ACCURACY
        # =====================================

        report["ai_accuracy"] = report["win_rate"]

        return report

    except Exception as e:

        print("PNL report error:", e)

        return None
