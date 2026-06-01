import time
import requests
from datetime import datetime
import pytz

from market import get_data
from db import create_paper_trade, get_open_trades, close_trade, save_signal
from config import SYMBOLS
from ai_engine import predict_signal

print(" bot_engine FILE LOADED")

# ✅ GLOBALS
last_signal_time = {}

# ✅ TIMEFRAMES
AUTO_TFS = ["1m", "3m", "5m", "15m", "30m", "1H"]
MANUAL_TFS = ["30m", "1H"]

# ✅ TELEGRAM
TELEGRAM_TOKEN = "8864549600:AAHaY2Q84VpkDBhYH6J0X4SNzpj-DLvGM_k"
AUTO_CHAT_ID = "-5211298112"
MANUAL_CHAT_ID = "-5287950499"

# ✅ UK TIME
def get_uk_time():
    return datetime.now(pytz.timezone("Europe/London"))


# =========================================
# ✅ TELEGRAM
# =========================================
def send_message(chat_id, message):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": message}
    )


# =========================================
# ✅ PROCESS SIGNAL
# =========================================
def process_timeframe(symbol, timeframe, table_name):

    df = get_data(symbol, timeframe, 40)
    if df.empty:
        return

    latest = float(df.iloc[0]['close'])
    avg = float(df['close'].mean())

    # ✅ VOLATILITY
    volatility = abs(latest - avg) / avg * 100

    # ✅ AI (AUTO FOR ALL TF)
    direction, ai_confidence = predict_signal(df, symbol, timeframe)

    if ai_confidence < 70:
        return

    signal_type = "LONG" if direction == "UP" else "SHORT"
    confidence = ai_confidence

    # ✅ COOLDOWN
    key = f"{symbol}_{timeframe}"
    if key in last_signal_time:
        if time.time() - last_signal_time[key] < 900:
            return
    last_signal_time[key] = time.time()

    # ✅ PREVENT DUPLICATE TRADES
    open_trades = get_open_trades()
    for t in open_trades:
        trade_symbol = t[1]
        trade_tf = t[4]  # timeframe column

    if trade_symbol == symbol and trade_tf == timeframe:
        print(f" Duplicate blocked {symbol} {timeframe}")
        return

    # ✅ CREATE TRADE (AUTO)
    create_paper_trade(symbol, signal_type, latest, 0, timeframe)

    # ✅ QUALITY
    if confidence >= 80:
        quality = " HIGH"
    elif confidence >= 70:
        quality = " GOOD"
    else:
        quality = " WEAK"

    # ✅ UK TIME FORMATTING
    uk_time = get_uk_time().strftime("%H:%M:%S")

    direction_text = "UP" if signal_type == "LONG" else "DOWN"

    # =====================================
    # ✅ SEND AUTO SIGNAL (ALL TF)
    # =====================================
    auto_msg = f"""
🤖 AI AUTO SIGNAL

Pair: {symbol}
Direction: {direction_text}
Entry: {latest}

AI Confidence: {confidence}%
Volatility: {round(volatility, 2)}%
Timeframe: {timeframe}
Time: {uk_time}

Signal Quality: {quality}

🚀 Trade placed automatically
"""
    send_message(AUTO_CHAT_ID, auto_msg)

    # =====================================
    # ✅ SEND MANUAL SIGNAL (30m,1H ONLY)
    # =====================================
    if timeframe in MANUAL_TFS and volatility >= 0.9:
        manual_msg = f"""
📡 MANUAL SIGNAL

Pair: {symbol}
TF: {timeframe}
Direction: {direction_text}

Volatility: {round(volatility,2)}%
Confidence: {confidence}%
Quality: {quality}
Time: {uk_time}

⚠️ Manual trade only
"""
        send_message(MANUAL_CHAT_ID, manual_msg)

    # ✅ SAVE
    save_signal(
        table_name,
        symbol,
        signal_type,
        confidence,
        latest,
        "AI",
        volatility
    )


# =========================================
# ✅ MONITOR TRADES
# =========================================
def monitor_trades():

    trades = get_open_trades()

    for trade in trades:
        try:
            trade_id, pair, side, entry = trade[0], trade[1], trade[2], float(trade[3])

            df = get_data(pair, "1m", 1)
            if df.empty:
                continue

            current = float(df.iloc[0]['close'])

            pnl = (
                (current - entry) / entry * 100
                if side == "LONG"
                else (entry - current) / entry * 100
            )

            if pnl >= 1 or pnl <= -1:
                close_trade(trade_id, current, round(pnl, 2))

        except:
            continue


# =========================================
# ✅ RUN BOT
# =========================================
def run_bot():

    print("💓 BOT RUNNING")

    for symbol in SYMBOLS:
        for tf, table in [
            ("1m", "signals_1M"),
            ("3m", "signals_3M"),
            ("5m", "signals_5M"),
            ("15m", "signals_15M"),
            ("30m", "signals_30M"),
            ("1H", "signals_1H"),
        ]:
            process_timeframe(symbol, tf, table)

        time.sleep(1)
