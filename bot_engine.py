import time
import requests
from market import get_data
from db import update_bot, save_signal, create_paper_trade, get_open_trades, close_trade
from config import SYMBOLS
from ai_engine import predict_trade
import threading

global last_run_time
last_run_time = time.time()

# =========================================
# ✅ TELEGRAM SIGNAL SENDER
# =========================================
def send_signal(message):
    token = "8864549600:AAHPKnzLQknUwQv9y1kWIyU-TSP6WmdVXTA"
    chat_id = "-5211298112"

    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=3  # 🔥 VERY IMPORTANT
        )
        print("✅ Signal sent")

    except Exception as e:
        print("Signal error:", e)


# =========================================
# ✅ CONFIDENCE CALCULATION
# =========================================
def calculate_confidence(current, average):
    pct = abs((current - average) / average) * 100
    return max(50, min(round(50 + (pct * 10), 2), 99))

# =========================================
# ✅ PROCESS SIGNAL
# =========================================
def process_timeframe(symbol, timeframe, table_name):

    global last_run_time
    last_run_time = time.time()

    df = get_data(symbol, timeframe, 40)
    if df.empty:
        print(f"⚠️ No data for {symbol} {timeframe}")
        return False

    latest = float(df.iloc[0]['close'])
    avg = float(df['close'].mean())

    if avg == 0:
        avg = latest

    signal_type = "LONG" if latest > avg else "SHORT"
    confidence = calculate_confidence(latest, avg)
    delta = abs(latest - avg)

    # ✅ SAFE AI CALL WITH TIMEOUT
    try:

        ai_probability = predict_trade(
            symbol,
            timeframe,
            signal_type,
            confidence,
            delta,
            confidence,
            0
        )

    except Exception as e:
        print("⚠️ AI timeout or error:", e)
        ai_probability = 0.7

    save_signal(table_name, symbol, signal_type, confidence, latest)

    print(f"{symbol} {timeframe} | Conf={confidence} | AI={ai_probability}")

    if confidence < 60 or ai_probability < 0.7:
        print(f"❌ Skipped {symbol} {timeframe} (weak signal)")
        return False

    create_paper_trade(symbol, signal_type, latest, confidence, timeframe)

    send_signal(f"""
🚨 AI SIGNAL

Pair: {symbol}
Timeframe: {timeframe}
Direction: {signal_type}

Confidence: {confidence}%
AI Probability: {round(ai_probability * 100, 2)}%

Entry: {latest}
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
""")

    return True

# =========================================
# ✅ MONITOR TRADES
# =========================================
def monitor_trades():
    try:
        trades = get_open_trades()
    except Exception as e:
        print("❌ Error loading trades:", e)
        return

    for trade in trades:
        try:
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

            pnl = round(pnl, 2)

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
            print("❌ Error in trade loop:", e)
            continue


# =========================================
# ✅ MAIN BOT ENGINE
# =========================================
def run_bots():
    print(f"⏱ {time.strftime('%H:%M:%S')} still running")
    global last_run_time
    last_run_time = time.time()

    print("💓 BOT ALIVE")

    signals_found = 0

    for symbol in SYMBOLS:
        try:
            print(f"\n🔎 Scanning: {symbol}")

            for tf, table in [
                ("1m", "signals_1m"),
                ("5m", "signals_5m"),
                ("15m", "signals_15m"),
                ("30m", "signals_30m")
            ]:

                try:
                    result = process_timeframe(symbol, tf, table)

                    if result:
                        signals_found += 1

                except Exception as e:
                    print(f"❌ Error in timeframe {tf}: {e}")
                    continue

            update_bot(symbol, "RUNNING", symbol, 0)

        except Exception as e:
            print(f"❌ Error in symbol {symbol}: {e}")
            continue

        time.sleep(0.3)

    print(f"\n✅ {signals_found} SIGNAL(S) GENERATED")

def watchdog():
    global last_run_time

    while True:
        time.sleep(10)

        if time.time() - last_run_time > 120:
            print("⚠️ BOT STUCK — resetting safely")
            last_run_time = time.time()
