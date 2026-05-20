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
