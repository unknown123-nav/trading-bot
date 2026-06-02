import time
import requests
from datetime import datetime
import pytz

from market import get_data
from db import create_paper_trade, get_open_trades, close_trade, save_signal
from config import SYMBOLS
from ai_engine import predict_signal

print("✅ bot_engine LOADED")

recent_symbols = {}
last_signal_time = {}

# ✅ TELEGRAM CONFIG
TELEGRAM_TOKEN = "8625282562:AAGNQZgdVK0mPYrXJ2GOAlc55HW74_5glak"
AUTO_CHAT_ID = "-5211298112"
MANUAL_CHAT_ID = "-5287950499"

MANUAL_TFS = ["30m", "1H"]

# ✅ UK TIME
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
# ✅ AUTO SIGNAL
# =========================================
def process_auto(symbol, timeframe, table_name):

    df = get_data(symbol, timeframe, 40)
    if df.empty:
        return

    latest = float(df.iloc[0]['close'])
    avg = float(df['close'].mean())
    volatility = abs(latest - avg) / avg * 100

    direction, ai_confidence = predict_signal(df, symbol, timeframe)

    # ✅ STRICT FILTERS
    if ai_confidence < 90:
        return

    if volatility < 1.0:
        return

    # ✅ LIMIT 1 SIGNAL PER SYMBOL (5 MIN)
    symbol_key = f"{symbol}_global"
    if symbol_key in recent_symbols:
        if time.time() - recent_symbols[symbol_key] < 300:
            return
    recent_symbols[symbol_key] = time.time()

    signal_type = "LONG" if direction == "UP" else "SHORT"
    direction_text = "UP" if signal_type == "LONG" else "DOWN"

    # ✅ CONFIDENCE
    confidence = (ai_confidence * 0.7) + (volatility * 20)
    confidence = max(60, min(confidence, 95))
    confidence = round(confidence, 2)

    take_profit = latest * (1.01 if signal_type == "LONG" else 0.99)
    stop_loss = latest * (0.99 if signal_type == "LONG" else 1.01)

    create_paper_trade(symbol, signal_type, latest, 1, timeframe, take_profit, stop_loss)

    print(f"✅ AUTO {symbol} {timeframe} | CONF: {confidence} | VOL: {round(volatility,2)}")

    uk_time = get_uk_time().strftime("%H:%M:%S")

    send_message(AUTO_CHAT_ID, f"""
🤖 AUTO SIGNAL

Pair: {symbol}
Direction: {direction_text}
Entry: {latest}

Confidence: {confidence}%
Volatility: {round(volatility,2)}%
Timeframe: {timeframe}
Time: {uk_time}

TP: {round(take_profit,4)}
SL: {round(stop_loss,4)}
""")

    save_signal(table_name, symbol, signal_type, confidence, latest, "AI", volatility, trade_source="AUTO")


# =========================================
# ✅ MANUAL SIGNAL
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

    # ✅ VERY STRICT FILTER
    if volatility < 3.0:
        return

    if abs(latest - avg) / avg * 100 < 1.5:
        return

    key = f"{symbol}_{timeframe}_MANUAL"
    if key in last_signal_time:
        if time.time() - last_signal_time[key] < 300:
            return

    last_signal_time[key] = time.time()

    direction = "UP" if latest > avg else "DOWN"
    signal_type = "LONG" if direction == "UP" else "SHORT"

    confidence = min(95, round(volatility * 40, 2))
    uk_time = get_uk_time().strftime("%H:%M:%S")

    print(f"✅ MANUAL {symbol} {timeframe} | CONF: {confidence}")

    send_message(MANUAL_CHAT_ID, f"""
📡 MANUAL SIGNAL

Pair: {symbol}
Direction: {direction}
Timeframe: {timeframe}

Volatility: {round(volatility,2)}%
Confidence: {confidence}%
Time: {uk_time}
""")

    save_signal(table_name, symbol, signal_type, confidence, latest, "AI", volatility, trade_source="MANUAL")


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

            if (side == "LONG" and current >= tp) or (side == "SHORT" and current <= tp):
                print(f"🎯 TP HIT → {pair}")
                close_trade(trade_id, current, round(pnl, 2))

            elif (side == "LONG" and current <= sl) or (side == "SHORT" and current >= sl):
                print(f"🛑 SL HIT → {pair}")
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
                ("5m", "signals_5M"),
                ("15m", "signals_15M"),
                ("30m", "signals_30M"),
                ("1H", "signals_1H"),
            ]:
                process_auto(symbol, tf, table)
                process_manual(symbol, tf, table)
                time.sleep(0.2)

        monitor_trades()

        time.sleep(2)
