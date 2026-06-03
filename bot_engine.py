import time
import requests
from datetime import datetime
import pytz

from market import get_data
from db import create_paper_trade, get_open_trades, close_trade, save_signal, save_telegram_log
from config import SYMBOLS
from ai_engine import predict_signal

print("✅ bot_engine LOADED")
processing = {}
recent_symbols = {}
last_signal_time = {}

TELEGRAM_TOKEN = "8625282562:AAGNQZgdVK0mPYrXJ2GOAlc55HW74_5glak"
AUTO_CHAT_ID = "-5211298112"
MANUAL_CHAT_ID = "-5287950499"

MANUAL_TFS = ["30m", "1H"]

def get_uk_time():
    return datetime.now(pytz.timezone("Europe/London"))

# ✅ TELEGRAM
def send_message(chat_id, message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": message}
        )
    except:
        print("❌ Telegram failed")

# =========================================
# ✅ AUTO (REAL TRADES ONLY)
# =========================================
def process_auto(symbol, timeframe, table_name):

    key = f"{symbol}-{timeframe}"

    if processing.get(key):
        return

    processing[key] = True

    try:
        df = get_data(symbol, timeframe, 40)
        if df.empty:
            return

        latest = float(df.iloc[0]['close'])
        avg = float(df['close'].mean())
        volatility = abs(latest - avg) / avg * 100

        direction, ai_confidence = predict_signal(df, symbol, timeframe)

        # ✅ SUPER STRICT RULES
        if ai_confidence < 95:
            return

        if volatility < 1.5:
            return

        # ✅ GLOBAL LIMIT
        symbol_key = f"{symbol}_global"
        if symbol_key in recent_symbols:
            if time.time() - recent_symbols[symbol_key] < 300:
                return

        signal_type = "LONG" if direction == "UP" else "SHORT"
        direction_text = "UP" if signal_type == "LONG" else "DOWN"

        confidence = round((ai_confidence * 0.7) + (volatility * 20), 2)
        confidence = max(60, min(confidence, 95))

        tp = latest * (1.01 if signal_type == "LONG" else 0.99)
        sl = latest * (0.99 if signal_type == "LONG" else 1.01)

        created = create_paper_trade(symbol, signal_type, latest, 1, timeframe, tp, sl)

        if not created:
            print(f" BLOCKED → {symbol} {timeframe}")
            return

        recent_symbols[symbol_key] = time.time()

        print(f" REAL TRADE → {symbol} {timeframe}")

        uk_time = get_uk_time().strftime("%H:%M:%S")

        message_text = f"""
🤖 AUTO TRADE STARTED

Pair: {symbol}
Direction: {direction_text}
Entry: {latest}

Confidence: {confidence}%
Volatility: {round(volatility,2)}%
Timeframe: {timeframe}
Time: {uk_time}

TP: {round(tp,4)}
SL: {round(sl,4)}
"""

        send_message(AUTO_CHAT_ID, message_text)

        save_signal(table_name, symbol, signal_type, confidence, latest, "AI", volatility, trade_source="AUTO")

        save_telegram_log(message_text, "AUTO_CHANNEL", "SENT")

    except Exception as e:
        print(f"❌ AUTO ERROR → {symbol} {timeframe}: {e}")
        time.sleep(1)


    finally:
        processing[key] = False
# =========================================
# ✅ MANUAL (NO TRADES)
# =========================================
def process_manual(symbol, timeframe, table_name):

    if timeframe not in MANUAL_TFS:
        return

    df = get_data(symbol, timeframe, 40)
    if df.empty:
        return

    latest = float(df.iloc[0]['close'])
    avg = float(df['close'].mean())
    volatility = abs(latest - avg) / avg * 100

    direction, ai_confidence = predict_signal(df, symbol, timeframe)

    # ✅ STRICT MANUAL RULES
    if ai_confidence < 90:
        return

    if volatility < 3.8:
        return

    key = f"{symbol}_{timeframe}_MANUAL"
    if key in last_signal_time:
        if time.time() - last_signal_time[key] < 300:
            return

    last_signal_time[key] = time.time()

    direction_text = direction
    signal_type = "LONG" if direction == "UP" else "SHORT"

    confidence = 95
    uk_time = get_uk_time().strftime("%H:%M:%S")

    message_text = f"""
📡 MANUAL SIGNAL

Pair: {symbol}
Direction: {direction_text}
Timeframe: {timeframe}

Volatility: {round(volatility,2)}%
Confidence: {confidence}%
Time: {uk_time}
"""

    send_message(MANUAL_CHAT_ID, message_text)

    save_signal(table_name, symbol, signal_type, confidence, latest, "AI", volatility, trade_source="MANUAL")

    save_telegram_log(message_text, "MANUAL_CHANNEL", "SENT")


# =========================================
# ✅ MONITOR TRADES
# =========================================
def monitor_trades():

    trades = get_open_trades()

    for trade in trades:
        try:
            trade_id = trade[0]
            pair = trade[1]
            side = trade[2]
            entry = float(trade[3])
            tf = trade[4]
            tp = float(trade[5])
            sl = float(trade[6])

            df = get_data(pair, tf, 1)
            if df.empty:
                continue

            current = float(df.iloc[0]['close'])

            pnl = (
                (current - entry) / entry * 100
                if side == "LONG"
                else (entry - current) / entry * 100
            )

            should_close = False

            if (side == "LONG" and current >= tp) or (side == "SHORT" and current <= tp):
                print(f" TP HIT → {pair}")
                should_close = True

            elif (side == "LONG" and current <= sl) or (side == "SHORT" and current >= sl):
                print(f" SL HIT → {pair}")
                should_close = True

            # ✅ SAFETY CHECK (CRITICAL)
            if should_close:
                conn = None
                try:
                    from db import get_connection
                    conn = get_connection()
                    cursor = conn.cursor()

                    cursor.execute("""
                        SELECT status FROM paper_trades WHERE id = %s
                    """, (trade_id,))
                    status = cursor.fetchone()

                    if not status or status[0] != "OPEN":
                        continue  # ✅ already closed → skip

                finally:
                    if conn:
                        conn.close()

                result = "WIN " if pnl > 0 else "LOSS "
                uk_time = get_uk_time().strftime("%H:%M:%S")
                message_text = f"""📊 TRADE CLOSED

Pair: {pair}
Side: {side}

Entry: {entry}
Exit: {current}

PnL: {round(pnl, 2)}%
Result: {result}

Time: {uk_time}
"""
                send_message(AUTO_CHAT_ID, message_text)
                save_telegram_log(message_text, "AUTO_CHANNEL", "CLOSED")
                close_trade(trade_id, current, round(pnl, 2))

        except Exception as e:
            print("❌ Monitor error:", e)
# =========================================
# ✅ RUN BOT
# =========================================
def run_bot():

    print("💓 BOT RUNNING")

    while True:
        for symbol in SYMBOLS:
            for tf, table in [
                ("1m", "signals_1M"),
                ("3m", "signals_3M"),
                ("5m", "signals_5M"),
                ("15m", "signals_15M"),
                ("30m", "signals_30M"),
                ("1H", "signals_1H"),
            ]:
                process_auto(symbol, tf, table)
                process_manual(symbol, tf, table)
                time.sleep(0.5)

        monitor_trades()

        time.sleep(3)
