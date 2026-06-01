import time
import requests

from market import get_data
from db import (
    create_paper_trade,
    get_open_trades,
    close_trade,
    save_signal
)
from config import SYMBOLS
from ai_engine import predict_signal

print(" bot_engine FILE LOADED")

#  GLOBALS
daily_signals_count = 0
last_reset_day = time.strftime("%Y-%m-%d")
last_signal_time = {}

# =========================================
#  TELEGRAM CONFIG
# =========================================
TELEGRAM_TOKEN = "8864549600:AAHaY2Q84VpkDBhYH6J0X4SNzpj-DLvGM_k"
AUTO_CHAT_ID = "-5211298112"
MANUAL_CHAT_ID = "-5287950499"

# =========================================
#  TELEGRAM SENDER
# =========================================
def send_signal(message, timeframe):

    if timeframe in ["5m", "15m"]:
        chat_id = AUTO_CHAT_ID
    else:
        chat_id = MANUAL_CHAT_ID

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": message}
    )


# =========================================
#  CANDLE PATTERN
# =========================================
def detect_candle_pattern(df):
    try:
        if len(df) < 2:
            return "UNKNOWN"

        last = df.iloc[0]
        prev = df.iloc[1]

        open_ = float(last['open'])
        close = float(last['close'])
        high = float(last['high'])
        low = float(last['low'])

        prev_open = float(prev['open'])
        prev_close = float(prev['close'])

        body = abs(close - open_)
        candle_range = high - low

        if body < candle_range * 0.1:
            return "DOJI"

        if close > open_ and prev_close < prev_open:
            if close > prev_open and open_ < prev_close:
                return "BULLISH ENGULFING"

        if close < open_ and prev_close > prev_open:
            if open_ > prev_close and close < prev_open:
                return "BEARISH ENGULFING"

        upper_wick = high - max(open_, close)
        lower_wick = min(open_, close) - low

        if upper_wick > body * 2:
            return "BEARISH PIN BAR"

        if lower_wick > body * 2:
            return "BULLISH PIN BAR"

        return "NORMAL"

    except:
        return "UNKNOWN"


# =========================================
#  PROCESS SIGNAL
# =========================================
def process_timeframe(symbol, timeframe, table_name):

    global daily_signals_count, last_reset_day

    #  RESET DAILY
    today = time.strftime("%Y-%m-%d")
    if today != last_reset_day:
        daily_signals_count = 0
        last_reset_day = today

    df = get_data(symbol, timeframe, 40)
    if df.empty:
        return

    latest = float(df.iloc[0]['close'])
    avg = float(df['close'].mean()) or latest

    #  VOLATILITY
    volatility = abs(latest - avg) / avg * 100

    #  DEFAULT CONF (manual only)
    confidence = max(55, min(55 + (volatility * 10), 99))

    print(f"DEBUG → {symbol} {timeframe} | vol={volatility:.2f} conf={confidence:.2f}")

    # =========================================
    #  AUTO (AI MODE)
    # =========================================
    if timeframe in ["5m", "15m"]:

        print(f" AI MODE → {symbol} {timeframe}")

        direction, ai_confidence = predict_signal(df)

        print(f"AI → {symbol} {timeframe} | {direction} {ai_confidence}")

        if ai_confidence < 70:
            return

        signal_type = "LONG" if direction == "UP" else "SHORT"
        confidence = ai_confidence

    # =========================================
    #  MANUAL (RULE MODE)
    # =========================================
    else:
        if volatility < 0.9 or confidence < 70:
            return

        signal_type = "LONG" if latest > avg else "SHORT"

    #  COOLDOWN (15 mins)
    key = f"{symbol}_{timeframe}"
    if key in last_signal_time:
        if time.time() - last_signal_time[key] < 900:
            return

    #  PREVENT DUPLICATE TRADES (AUTO ONLY)
    if timeframe in ["5m", "15m"]:
        open_trades = get_open_trades()

        for t in open_trades:
            if t[1] == symbol:
                print(f" Trade already open for {symbol}")
                return

    last_signal_time[key] = time.time()

    #  CREATE TRADE (AUTO ONLY)
    if timeframe in ["5m", "15m"]:
        create_paper_trade(symbol, signal_type, latest, 0, timeframe)

    #  OUTPUT DIRECTION
    direction = "UP" if signal_type == "LONG" else "DOWN"

    #  SIGNAL QUALITY
    if confidence >= 80:
        quality = " HIGH"
    elif confidence >= 70:
        quality = " GOOD"
    else:
        quality = " WEAK"

    # =========================================
    #  MESSAGE OUTPUT
    # =========================================
    if timeframe in ["5m", "15m"]:
        message = f"""
 AI AUTO SIGNAL

Pair: {symbol}
Direction: {direction}
Entry: {latest}

AI Confidence: {round(confidence)}%
Signal Quality: {quality}

 Trade placed automatically
"""
    else:
        message = f"""
 MANUAL SIGNAL

Pair: {symbol}
Direction: {direction}
Entry: {latest}

Volatility: {round(volatility, 2)}%
Confidence: {round(confidence)}%
Signal Quality: {quality}

 Manual trade — no auto execution
"""

    send_signal(message, timeframe)
    time.sleep(0.3)

    save_signal(
        table_name,
        symbol,
        signal_type,
        confidence,
        latest,
        detect_candle_pattern(df),
        volatility
    )


# =========================================
#  MONITOR TRADES
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
#  RUN BOT
# =========================================
def run_bot():

    print("💓 BOT RUNNING")

    for symbol in SYMBOLS:
        for tf, table in [
            ("5m", "signals_5M"),
            ("15m", "signals_15M"),
            ("30m", "signals_30M"),
            ("1H", "signals_1H")
        ]:
            process_timeframe(symbol, tf, table)

        time.sleep(1)
