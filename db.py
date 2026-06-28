import mysql.connector
from config import DB_CONFIG
from datetime import datetime


ALLOWED_SIGNAL_TABLES = [
    "signals_1M", "signals_3M", "signals_5M",
    "signals_15M", "signals_30M", "signals_1H"
]

# =========================================
#  CONNECTION
# =========================================
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# =========================================
# GET LATEST SIGNALS (FOR TELEGRAM)
# =========================================
def get_latest_signals(source=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if source:
            cursor.execute("""
                SELECT pair, direction, confidence
                FROM signals_15M
                WHERE trade_source = %s
                ORDER BY id DESC
                LIMIT 5
            """, (source,))
        else:
            cursor.execute("""
                SELECT pair, direction, confidence
                FROM signals_15M
                ORDER BY id DESC
                LIMIT 5
            """)

        return cursor.fetchall()

    except Exception as e:
        print(" Latest signal error:", e)
        return []

    finally:
        cursor.close()
        conn.close()
# =========================================
#  SAVE SIGNAL
# =========================================
def save_signal(table, pair, direction, confidence, entry, pattern, volatility, trade_source):

    if table not in ALLOWED_SIGNAL_TABLES:
        print(f" Invalid table: {table}")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        print(f"Saving signal into {table}")

        cursor.execute(f"""
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
        """, (
            pair,
            direction,
            confidence,
            entry,
            pattern,
            volatility,
            table.replace("signals_", ""),
            trade_source
        ))

        print("INSERT successful")
        conn.commit()
        print(f" Saved signal → {table} | {pair}")

    except Exception as e:
        import traceback
        traceback.print_exc()

    finally:
        cursor.close()
        conn.close()


def create_paper_trade(symbol, side, entry, qty, timeframe, tp, sl):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, created_at FROM paper_trades
            WHERE pair = %s AND timeframe = %s AND status = 'OPEN'
            LIMIT 1
        """, (symbol, timeframe))

        row = cursor.fetchone()

        if row:
            trade_id, created_at = row
            diff = (datetime.now() - created_at).total_seconds()

            if diff < 300:
                print(f" BLOCKED → {symbol} {timeframe} (existing open trade)")
                return False

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
        print(f" Trade created → {symbol} {timeframe}")
        return True   

    except Exception as e:
        print(" Trade creation error:", e)
        return False

    finally:
        cursor.close()
        conn.close()

# =========================================
#  GET OPEN TRADES
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
        print(" Open trade fetch error:", e)
        return []

    finally:
        cursor.close()
        conn.close()

# =========================================
#  CLOSE TRADE
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
            WHERE id = %s AND status = 'OPEN'
        """, (current_price, pnl, trade_id))

        if cursor.rowcount == 0:
            
            return

        conn.commit()
        print(f" Trade {trade_id} CLOSED")

    except Exception as e:
        print("❌ Close trade error:", e)

    finally:
        cursor.close()
        conn.close()


# =========================================
#  TELEGRAM FUNCTIONS
# =========================================
def get_active_trades():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT pair, side FROM paper_trades
            WHERE status = 'OPEN'
        """)
        return cursor.fetchall()
    except:
        return []
    finally:
        conn.close()


def get_pnl_report():
    return {
        "win_rate": 0,
        "active_trades": 0,
        "signals": 0,
        "ai_accuracy": 0
    }

# =========================================
# ✅ TELEGRAM LOGS
# =========================================
def save_telegram_log(message, channel_name, status="SENT"):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO telegram_logs (message, channel_name, status)
            VALUES (%s, %s, %s)
        """, (message, channel_name, status))
        conn.commit()

    except Exception as e:
        print("❌ Telegram log error:", e)

    finally:
        cursor.close()
        conn.close()

# =========================================
# ✅ TELEGRAM CONVERSATIONS
# =========================================
def save_conversation(message_id, pair, user_msg, bot_msg):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO telegram_conversations
            (telegram_message_id, pair_name, user_message, bot_response)
            VALUES (%s, %s, %s, %s)
        """, (message_id, pair, user_msg, bot_msg))

        conn.commit()

    except Exception as e:
        print(" Conversation save error:", e)

    finally:
        cursor.close()
        conn.close()

def get_manual_trades():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT pair, direction
            FROM manual_trades
            WHERE status = 'OPEN'
        """)
        return cursor.fetchall()
    except Exception as e:
        print("Manual trade error:", e)
        return []
    finally:
        cursor.close()
        conn.close()
