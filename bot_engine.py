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

print("✅ bot_engine FILE LOADED")

# ✅ GLOBALS
daily_signals_count = 0
last_reset_day = time.strftime("%Y-%m-%d")


# =========================================
# ✅ TELEGRAM CONFIG
# =========================================
AUTO_TOKEN = "8864549600:AAHaY2Q84VpkDBhYH6J0X4SNzpj-DLvGM_k"
AUTO_CHAT_ID = "-5211298112"

MANUAL_TOKEN = "8429745559:AAEK3E7-ihSMdNNlv8SH3GlKTFsuYxG45rA"
MANUAL_CHAT_ID = "-5287950499"


# =========================================
# ✅ TELEGRAM SENDER
# =========================================
def send_signal(message, timeframe):

    if timeframe in ["5m", "15m"]:
        token = AUTO_TOKEN
        chat_id = AUTO_CHAT_ID
    else:
        token = MANUAL_TOKEN
        chat_id = MANUAL_CHAT_ID

    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=3
        )
    except Exception as e:
        print("Signal error:", e)


# =========================================
# ✅ CANDLE PATTERN DETECTION
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

        # ✅ DOJI
        if body < (candle_range * 0.1):
            return "DOJI"

        # ✅ BULLISH ENGULFING
        if close > open_ and prev_close < prev_open:
            if close > prev_open and open_ < prev_close:
                return "BULLISH ENGULFING"

        # ✅ BEARISH ENGULFING
        if close < open_ and prev_close > prev_open:
            if open_ > prev_close and close < prev_open:
                return "BEARISH ENGULFING"

        # ✅ PIN BAR
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
# ✅ PROCESS SIGNAL
# =========================================
def process_timeframe(symbol, timeframe, table_name):

    global daily_signals_count, last_reset_day

    # ✅ RESET DAILY
    today = time.strftime("%Y-%m-%d")
    if today != last_reset_day:
        daily_signals_count = 0
        last_reset_day = today

    # ✅ LIMIT SIGNALS
    if daily_signals_count >= 20:
        return

    df = get_data(symbol, timeframe, 40)
    if df.empty:
        return

    latest = float(df.iloc[0]['close'])
    avg = float(df['close'].mean()) or latest

    signal_type = "LONG" if latest > avg else "SHORT"

    # ✅ VOLATILITY
    volatility = abs(latest - avg) / avg * 100
    if volatility < 0.5:
        return

    # ✅ CONFIDENCE (MIN 55 NOW ✅)
    confidence = max(55, min(55 + (volatility * 10), 99))

    # ✅ CANDLE PATTERN
    candle_pattern = detect_candle_pattern(df)

    # ✅ OPTIONAL FILTER (recommended)
    if candle_pattern == "DOJI":
        return

    # ✅ CHECK EXISTING TRADES
    open_trades = get_open_trades()
    for t in open_trades:
        if t[1] == symbol:
            return

    # ✅ CREATE TRADE
    create_paper_trade(symbol, signal_type, latest, 0, timeframe)

    # ✅ MESSAGE
    direction = "UP" if signal_type == "LONG" else "DOWN"

    message = f"""
📊 TRADE SIGNAL

Pair: {symbol}
Direction: {direction}
Entry: {latest}
Pattern: {candle_pattern}
Confidence: {round(confidence)}%
Volatility: {round(volatility, 2)}%

Timeframe: {timeframe}
Date: {time.strftime('%d-%m-%Y')}
Time: {time.strftime('%H:%M:%S')}
"""

    # ✅ SEND
    send_signal(message, timeframe)

    print(f"Trying to save signal: {symbol} {timeframe}")

    # ✅ SAVE (✅ FIXED ARGUMENTS)
    save_signal(
        table_name,
        symbol,
        signal_type,
        confidence,
        latest,
        candle_pattern,
        volatility
    )

    daily_signals_count += 1


# =========================================
# ✅ MONITOR TRADES
# =========================================
def monitor_trades():
    trades = get_open_trades()

    for trade in trades:
        try:
            if len(trade) < 4:
                continue

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

            if pnl >= 2 or pnl <= -2:
                close_trade(trade_id, current, round(pnl, 2))

        except Exception:
            continue


# =========================================
# ✅ RUN BOT
# =========================================
def run_bot():

    print("💓 BOT ALIVE")

    for symbol in SYMBOLS:
        try:
            for tf, table in [
                ("5m", "signals_5M"),
                ("15m", "signals_15M"),
                ("30m", "signals_30M"),
                ("1H", "signals_1H")
            ]:
                process_timeframe(symbol, tf, table)

        except Exception as e:
            print("Error:", e)

        time.sleep(2)
