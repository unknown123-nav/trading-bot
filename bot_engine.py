import time
import requests
from market import get_data
from db import update_bot, save_signal, create_paper_trade, get_open_trades, close_trade
from config import SYMBOLS
from ai_engine import predict_trade


# =========================================
# ✅ TELEGRAM SIGNAL SENDER
# =========================================
def send_signal(message):
    token = "8864549600:AAHPKnzLQknUwQv9y1kWIyU-TSP6WmdVXTA"
    chat_id = "-5211298112"

    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message}
        )
        print("✅ Signal sent")
        time.sleep(0.5)

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

    df = get_data(symbol, timeframe, 40)
    if df.empty:
        return

    latest = float(df.iloc[0]['close'])
    avg = float(df['close'].mean())

    signal = "LONG" if latest > avg else "SHORT"
    confidence = calculate_confidence(latest, avg)

    delta = abs(latest - avg)

    try:
        ai_probability = predict_trade(
            symbol,
            timeframe,
            signal,
            confidence,
            delta,
            confidence,
            0
        )
    except:
        ai_probability = 0.5  # ✅ fallback so signal still works

    save_signal(table_name, symbol, signal, confidence, latest)

    print(f"{symbol} {timeframe} | Conf={confidence} | AI={ai_probability}")

    # ✅ VERY LIGHT FILTER (always produces signals)
    if confidence < 50:
        return

    # ✅ CREATE TRADE (no blocking)
    create_paper_trade(symbol, signal, latest, confidence, timeframe)

    # ✅ SEND SIGNAL ALWAYS
    send_signal(f"""
🚨 AI SIGNAL

Pair: {symbol}
Timeframe: {timeframe}
Direction: {signal}

Confidence: {confidence}%
AI Probability: {round(ai_probability * 100, 2)}%

Entry: {latest}
Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
""")

    time.sleep(0.2)


# =========================================
# ✅ MONITOR TRADES
# =========================================
def monitor_trades():

    trades = get_open_trades()

    for trade in trades:

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

        # ✅ slightly relaxed exits
        if pnl >= 2 or pnl <= -2:

            close_trade(trade_id, current, pnl)

            send_signal(f"""
✅ TRADE CLOSED

Pair: {pair}
Direction: {side}

PNL: {pnl}%

Time: {time.strftime('%H:%M:%S')}
""")


# =========================================
# ✅ MAIN BOT ENGINE
# =========================================
def run_bots():

    for symbol in SYMBOLS:

        print(f"Running {symbol}")

        process_timeframe(symbol, "1m", "signals_1m")
        process_timeframe(symbol, "3m", "signals_3m")
        process_timeframe(symbol, "5m", "signals_5m")
        process_timeframe(symbol, "15m", "signals_15m")
        process_timeframe(symbol, "30m", "signals_30m")
        process_timeframe(symbol, "1h", "signals_1h")

        update_bot(symbol, "RUNNING", symbol, 0)

        time.sleep(0.3)
