import mysql.connector

from config import DB_CONFIG


# =========================================
# CREATE NEW CONNECTION
# =========================================

def get_connection():

    return mysql.connector.connect(
        **DB_CONFIG
    )


# =========================================
# SAVE SIGNAL
# =========================================

def save_signal(
    table,
    pair,
    signal_type,
    confidence,
    price
):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        query = f"""
        INSERT INTO {table}
        (
            pair_name,
            signal_type,
            confidence,
            entry_price,
            created_at
        )
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

        print(
            "Signal save error:",
            e
        )

    finally:

        cursor.close()

        conn.close()


# =========================================
# UPDATE BOT STATUS
# =========================================

def update_bot(
    bot_name,
    status,
    pair,
    pnl
):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        query = """
        INSERT INTO bot_status
        (
            bot_name,
            status,
            current_pair,
            pnl_today,
            last_heartbeat
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            NOW()
        )

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

        print(
            "Bot update error:",
            e
        )

    finally:

        cursor.close()

        conn.close()


# =========================================
# CREATE PAPER TRADE
# =========================================

def create_paper_trade(
    pair,
    side,
    entry_price,
    confidence,
    timeframe
):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        # =====================================
        # CHECK EXISTING OPEN TRADE
        # =====================================

        check_query = """
        SELECT id
        FROM paper_trades
        WHERE
            pair = %s
            AND timeframe = %s
            AND status = 'OPEN'
        LIMIT 1
        """

        cursor.execute(check_query, (
            pair,
            timeframe
        ))

        existing_trade = cursor.fetchone()

        # =====================================
        # SKIP DUPLICATE TRADE
        # =====================================

        if existing_trade:

            print(
                f"Trade already open: "
                f"{pair} {timeframe}"
            )

            return

        # =====================================
        # CREATE TRADE
        # =====================================

        query = """
        INSERT INTO paper_trades
        (
            pair,
            side,
            entry_price,
            quantity,
            leverage,
            timeframe,
            ai_confidence,
            trade_source,
            status,
            created_at
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            NOW()
        )
        """

        cursor.execute(query, (
            pair,
            side,
            entry_price,
            1,
            1,
            timeframe,
            confidence,
            "AI",
            "OPEN"
        ))

        conn.commit()

        print(
            f"Trade created: "
            f"{pair} {side}"
        )

    except Exception as e:

        print(
            "Trade creation error:",
            e
        )

    finally:

        cursor.close()

        conn.close()


# =========================================
# GET LATEST SIGNALS
# =========================================

def get_latest_signals():

    conn = get_connection()

    cursor = conn.cursor()

    try:

        query = """
        SELECT
            pair_name,
            signal_type,
            confidence
        FROM signals_1m
        ORDER BY created_at DESC
        LIMIT 5
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        return rows

    except Exception as e:

        print(
            "Signal fetch error:",
            e
        )

        return []

    finally:

        cursor.close()

        conn.close()


# =========================================
# GET ACTIVE TRADES
# =========================================

def get_active_trades():

    conn = get_connection()

    cursor = conn.cursor()

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

        print(
            "Trade fetch error:",
            e
        )

        return []

    finally:

        cursor.close()

        conn.close()


# =========================================
# GET PNL REPORT
# =========================================

def get_pnl_report():

    conn = get_connection()

    cursor = conn.cursor()

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
        # WINNING TRADES
        # =====================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM paper_trades
            WHERE pnl > 0
        """)

        wins = cursor.fetchone()[0]

        # =====================================
        # TOTAL CLOSED TRADES
        # =====================================

        cursor.execute("""
            SELECT COUNT(*)
            FROM paper_trades
            WHERE pnl IS NOT NULL
        """)

        total = cursor.fetchone()[0]

        # =====================================
        # WIN RATE
        # =====================================

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

        print(
            "PNL report error:",
            e
        )

        return None

    finally:

        cursor.close()

        conn.close()


# =========================================
# GET OPEN TRADES
# =========================================
def get_open_trades():

    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        SELECT id, pair, side, entry_price
        FROM paper_trades
        WHERE status = 'OPEN'
        """

        cursor.execute(query)
        return cursor.fetchall()

    except Exception as e:
        print("Open trade fetch error:", e)
        return []

    finally:
        cursor.close()
        conn.close()

# =========================================
# CLOSE TRADE
# =========================================
def close_trade(trade_id, current_price, pnl):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE paper_trades
            SET 
                current_price = %s,
                pnl = %s,
                status = 'CLOSED',
                closed_at = NOW()
            WHERE id = %s
        """, (current_price, pnl, trade_id))

        conn.commit()
        print(f"✅ Trade {trade_id} closed and saved")

    except Exception as e:
        print("Close trade error:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
