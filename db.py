import mysql.connector
from config import DB_CONFIG
from datetime import datetime

# ✅ ALLOWED TABLES (protects SQL injection)
ALLOWED_SIGNAL_TABLES = [
    "signals_1M", "signals_3M", "signals_5M",
    "signals_15M", "signals_30M", "signals_1H"
]

# =========================================
# ✅ CREATE CONNECTION
# =========================================
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# =========================================
# ✅ SAVE SIGNAL (SAFE)
# =========================================
def save_signal(table, pair, direction, confidence, entry, pattern, volatility, trade_source):

    if table not in ALLOWED_SIGNAL_TABLES:
        print(f"❌ Invalid table: {table}")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = f"""
        INSERT INTO {table} (
            pair,
            direction,
            confidence,
            entry_price,
            pattern,
            volatility,
            timeframe,
            trade_source
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            pair,
            direction,
            confidence,
            entry,
            pattern,
            volatility,
            table.replace("signals_", ""),  # timeframe
            trade_source
        ))

        conn.commit()
        print(f"✅ Saved signal → {table} | {pair}")

    except Exception as e:
        print("❌ Signal save error:", e)

    finally:
        cursor.close()
        conn.close()

# =========================================
# ✅ CREATE PAPER TRADE
# =========================================
def create_paper_trade(symbol, side, entry, qty, timeframe, tp, sl):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ✅ check existing open trade
        cursor.execute("""
            SELECT id, created_at FROM paper_trades
            WHERE pair = %s AND timeframe = %s AND status = 'OPEN'
            LIMIT 1
        """, (symbol, timeframe))

        row = cursor.fetchone()

        if row:
            trade_id, created_at = row

            diff = (datetime.now() - created_at).total_seconds()

            # ✅ allow new trade if older than 5 minutes
            if diff < 300:
                print(f"⚠️ Trade still active: {symbol} {timeframe}")
                return

            else:
                print(f"♻️ Old trade ignored → opening new one")

        # ✅ insert new trade
        cursor.execute("""
            INSERT INTO paper_trades (
                pair,
                side,
                entry_price,
                quantity,
                timeframe,
                take_profit,
                stop_loss,
                trade_source,
                status,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'OPEN', NOW())
        """, (
            symbol,
            side,
            entry,
            qty,
            timeframe,
            tp,
            sl,
            "AI"
        ))

        conn.commit()
        print(f"✅ Trade created → {symbol} {timeframe}")

    except Exception as e:
        print("❌ Trade creation error:", e)

    finally:
        cursor.close()
        conn.close()

# =========================================
# ✅ GET OPEN TRADES
# =========================================
def get_open_trades():

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, pair, side, entry_price, timeframe, take_profit, stop_loss
            FROM paper_trades
            WHERE status = 'OPEN'
        """)
        return cursor.fetchall()

    except Exception as e:
        print("❌ Open trade fetch error:", e)
        return []

    finally:
        cursor.close()
        conn.close()

# =========================================
# ✅ CLOSE TRADE
# =========================================
def close_trade(trade_id, current_price, pnl):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE paper_trades
            SET 
                exit_price = %s,
                pnl = %s,
                status = 'CLOSED',
                closed_at = NOW()
            WHERE id = %s
        """, (current_price, pnl, trade_id))

        conn.commit()
        print(f"✅ Trade {trade_id} CLOSED")

    except Exception as e:
        print("❌ Close trade error:", e)

    finally:
        cursor.close()
        conn.close()
