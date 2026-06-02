import time
import requests
from datetime import datetime
import pytz

from market import get_data
from db import create_paper_trade, get_open_trades, close_trade, save_signal
from config import SYMBOLS
from ai_engine import predict_signal

print("✅ bot_engine LOADED")

# ✅ TELEGRAM CONFIG
TELEGRAM_TOKEN = "8780022222:AAEyVNVseCqJ--tjwNv5nvcbxl4goeFQgC8"
AUTO_CHAT_ID = "-5211298112"
MANUAL_CHAT_ID = "-5287950499"

# ✅ GLOBALS
last_signal_time = {}

AUTO_TFS = ["1m", "3m", "5m", "15m", "30m", "1H"]
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

    if ai_confidence < 70:
        return

    signal_type = "LONG" if direction == "UP" else "SHORT"
    direction_text = "UP" if signal_type == "LONG" else "DOWN"

    key = f"{symbol}_{timeframe}_AUTO"

    # ✅ cooldown (5 min)
    if key in last_signal_time and time.time() - last_signal_time[key] < 300:
        return

    last_signal_time[key] = time.time()

    # ✅ better confidence formula
    confidence = (ai_confidence * 0.7) + (volatility * 20)
    confidence = max(60, min(confidence, 95))
    confidence = round(confidence, 2)

    # ✅ TP / SL
    take_profit = latest * (1.01 if signal_type == "LONG" else 0.99)
    stop_loss = latest * (0.99 if signal_type == "LONG" else 1.01)

    # ✅ create trade
    create_paper_trade(symbol, signal_type, latest, 1, timeframe, take_profit, stop_loss)

    print(f"✅ AUTO SIGNAL {symbol} {timeframe} | CONF: {confidence}% | VOL: {round(volatility,2)}%")

    uk_time = get_uk_time().strftime("%H:%M:%S")

    # ✅ TELEGRAM AUTO
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

🚀 Trade placed automatically
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

    if volatility < 0.9:
        return

    key = f"{symbol}_{timeframe}_MANUAL"

    if key in last_signal_time and time.time() - last_signal_time[key] < 300:
        return

    last_signal_time[key] = time.time()

    direction = "UP" if latest > avg else "DOWN"
    direction_text = direction
    signal_type = "LONG" if direction == "UP" else "SHORT"

    # ✅ volatility-based confidence
    confidence = min(95, round(volatility * 40, 2))

    uk_time = get_uk_time().strftime("%H:%M:%S")

    print(f"✅ MANUAL SIGNAL {symbol} {timeframe} | CONF: {confidence}% | VOL: {round(volatility,2)}%")

    send_message(MANUAL_CHAT_ID, f"""
📡 MANUAL SIGNAL

Pair: {symbol}
Direction: {direction_text}
Timeframe: {timeframe}

Volatility: {round(volatility,2)}%
Confidence: {confidence}%
Time: {uk_time}

⚠️ Manual trade only
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
            tp = float(trade[5])
            sl = float(trade[6])

            df = get_data(pair, "1m", 1)
            if df.empty:
                continue

            current = float(df.iloc[0]['close'])

            pnl = (
                (current - entry) / entry * 100
                if side == "LONG"
                else (entry - current) / entry * 100
            )

            # ✅ TP
            if (side == "LONG" and current >= tp) or (side == "SHORT" and current <= tp):
                print(f"🎯 TP HIT → {pair}")
                close_trade(trade_id, current, round(pnl, 2))

            # ✅ SL
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
                ("1m", "signals_1M"),
                ("3m", "signals_3M"),
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
