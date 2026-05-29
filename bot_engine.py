import time
import requests
import multiprocessing

from market import get_data
from db import (
    update_bot,
    save_signal,
    create_paper_trade,
    get_open_trades,
    close_trade
)
from config import SYMBOLS
from ai_engine import predict_trade


last_run_time = time.time()

# =========================================
# ✅ TELEGRAM SIGNAL
# =========================================
def send_signal(message):
    token = "8864549600:AAHaY2Q84VpkDBhYH6J0X4SNzpj-DLvGM_k"
    chat_id = "-5211298112"

    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=3
        )
    except Exception as e:
        print("Signal error:", e)


# =========================================
# ✅ CONFIDENCE
# =========================================
def calculate_confidence(current, avg):
    pct = abs((current - avg) / avg) * 100
    return max(50, min(round(50 + (pct * 10), 2), 99))


# =========================================
# ✅ SAFE AI (PROCESS BASED)
# =========================================
def run_ai(queue, symbol, timeframe, signal_type, confidence, delta):
    try:
        res = predict_trade(
            symbol, timeframe,
            signal_type,
            confidence,
            delta,
            confidence,
            0
        )
        queue.put(res)
    except:
        queue.put(0.7)


# =========================================
# ✅ PROCESS SIGNAL
# =========================================
def process_timeframe(symbol, timeframe, table_name):
    global last_run_time
    last_run_time = time.time()

    df = get_data(symbol, timeframe, 40)
    if df.empty:
        return False

    latest = float(df.iloc[0]['close'])
    avg = float(df['close'].mean()) or latest

    signal_type = "LONG" if latest > avg else "SHORT"
    confidence = calculate_confidence(latest, avg)
    delta = abs(latest - avg)

    # ✅ AI SAFE EXECUTION
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(
        target=run_ai,
        args=(queue, symbol, timeframe, signal_type, confidence, delta)
    )

    p.start()
    p.join(timeout=2)

    if p.is_alive():
        print(f"⚠️ AI TIMEOUT → {symbol} {timeframe}")
        p.terminate()
        p.join()
        ai_probability = 0.7
    else:
        try:
            ai_probability = queue.get_nowait()
        except:
            ai_probability = 0.7

    save_signal(table_name, symbol, signal_type, confidence, latest)

    print(f"{symbol} {timeframe} | Conf={confidence} | AI={ai_probability}")

    # ✅ FILTER
    if confidence < 60 or ai_probability < 0.7:
        return False

    # ✅ LIMIT TRADES
    open_trades = get_open_trades()

    if len(open_trades) > 20:
        print("⚠️ Too many trades")
        return False

    # ✅ PREVENT DUPLICATES
    for t in open_trades:
        if t[1] == symbol:
            print(f"⚠️ Trade exists: {symbol}")
            return False

    # ✅ CREATE TRADE
    create_paper_trade(symbol, signal_type, latest, confidence, timeframe)

    send_signal(f"""
🚨 AI SIGNAL

Pair: {symbol}
Timeframe: {timeframe}
Direction: {signal_type}

Confidence: {confidence}%
AI: {round(ai_probability * 100, 2)}%
Entry: {latest}
Time: {time.strftime('%H:%M:%S')}
""")

    return True


# =========================================
# ✅ MONITOR TRADES
# =========================================
def monitor_trades():
    try:
        trades = get_open_trades()
    except:
        return

    for trade in trades:
        try:
            # ✅ PROTECT AGAINST BAD ROWS
            if len(trade) < 4:
                print("⚠️ Skipping bad trade row:", trade)
                continue

            trade_id = trade[0]
            pair = trade[1]
            side = trade[2]
            entry = float(trade[3])

            df = get_data(pair, "1m", 1)
            if df.empty:
                continue

            current = float(df.iloc[0]['close'])

            pnl = (
                (current - entry) / entry * 100
                if side == "LONG"
                else (entry - current) / entry * 100
            )

            pnl = round(pnl, 4)

            if pnl >= 2 or pnl <= -2:
                close_trade(trade_id, current, pnl)

                send_signal(f"""
✅ TRADE CLOSED

Pair: {pair}
Direction: {side}
PNL: {pnl}%
Time: {time.strftime('%H:%M:%S')}
""")

        except Exception as e:
            print("Trade error:", e)
            continue

# =========================================
# ✅ RUN BOT
# =========================================
def run_bots():
    global last_run_time
    last_run_time = time.time()

    print("💓 BOT ALIVE")

    for symbol in SYMBOLS:
        try:
            for tf, table in [
                ("1m", "signals_1m"),
                ("5m", "signals_5m"),
                ("15m", "signals_15m")
            ]:
                process_timeframe(symbol, tf, table)

        except Exception as e:
            print("Error:", e)

        time.sleep(0.3)


# =========================================
# ✅ WATCHDOG
# =========================================
def watchdog():
    global last_run_time

    while True:
        time.sleep(10)

        if time.time() - last_run_time > 120:
            print("⚠️ BOT RECOVERED")
            last_run_time = time.time()

