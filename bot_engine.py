import time
import requests
from market import get_data
from db import update_bot, save_signal
from config import SYMBOLS
from db import create_paper_trade
from db import get_open_trades
from db import close_trade
from ai_engine import predict_trade

# ✅ GLOBAL LIMITS
signal_count = 0
symbol_used = {}


# =========================================
# ✅ TELEGRAM SIGNAL SENDER
# =========================================
def send_signal(message):
    token = "8864549600:AAH8S3USLHU6mOHSbcfxsMdrjYn47TXGCBY"
    chat_id = "-5211298112"

    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message}
        )
        time.sleep(1)  # ✅ prevent API overload
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

    global signal_count, symbol_used

    if signal_count >= 8:
        return

    if symbol in symbol_used:
        return

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
        ai_probability = 0

    save_signal(table_name, symbol, signal, confidence, latest)

    print(f"{symbol} {timeframe} | Confidence={confidence} | AI={ai_probability}")

    # ✅ RELAXED FILTER (IMPORTANT)
    if confidence < 55 or ai_probability <= 0.6:
        print(f"❌ Skipped {symbol} {timeframe}")
        return

    open_trades = get_open_trades()
    # ✅ prevent duplicate pair trades
    if symbol in [[1] for t in open_trades]:
        return

#     # ✅ IF MAX TRADES → SEND SIGNAL ONLY
#     if len(open_trades) >= 14:
#         print("⚠️ Max open trades reached — sending signal only")

#         send_signal(f"""
# 🚨 AI SIGNAL (NO TRADE)

# Pair: {symbol}
# Timeframe: {timeframe}
# Direction: {signal}

# Confidence: {confidence}%
# AI Probability: {round(ai_probability * 100, 2)}%

# ⚠️ Trade skipped (limit reached)
# Time: {time.strftime('%H:%M:%S')}
# """)

#         return

    # ✅ CREATE TRADE
    create_paper_trade(symbol, signal, latest, confidence, timeframe)

    # ✅ SEND NORMAL SIGNAL
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

    symbol_used[symbol] = True
    signal_count += 1

    time.sleep(0.4)


# =========================================
# ✅ MONITOR TRADES (CONTROLLED)
# =========================================
def monitor_trades():

    trades = get_open_trades()
    close_count = 0

    for trade in trades:

        # ✅ LIMIT CLOSURES PER CYCLE
        if close_count >= 2:
            return

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

        if pnl >= 2 or pnl <= -1:

            close_trade(trade_id, current, pnl)

            message = f"""
✅ TRADE CLOSED

Pair: {pair}
Direction: {side}

PNL: {pnl}%

Time: {time.strftime('%H:%M:%S')}
"""

            send_signal(message)

            close_count += 1


# =========================================
# ✅ MAIN BOT ENGINE
# =========================================
def run_bots():

    global signal_count, symbol_used

    signal_count = 0
    symbol_used = {}

    for symbol in SYMBOLS:

        print(f"Running {symbol}")

        # ✅ ALL TIMEFRAMES (teacher requirement ✅)
        process_timeframe(symbol, "1m", "signals_1m")
        time.sleep(0.2)
        
        process_timeframe(symbol, "3m", "signals_3m")
        time.sleep(0.2)
        
        process_timeframe(symbol, "5m", "signals_5m")
        time.sleep(0.2)
        
        process_timeframe(symbol, "15m", "signals_15m")
        time.sleep(0.2)
        
        process_timeframe(symbol, "30m", "signals_30m")
        time.sleep(0.2)
        
        process_timeframe(symbol, "1h", "signals_1h")

        update_bot(symbol, "RUNNING", symbol, 0)

        time.sleep(0.2)  # ✅ spread workload
