import time
import requests
from datetime import datetime
import pytz

from market import get_data
from db import create_paper_trade, get_open_trades, close_trade, save_signal
from config import SYMBOLS
from ai_engine import predict_signal

print("🚀 bot_engine LOADED")

# ✅ GLOBALS
last_signal_time = {}

AUTO_TFS = ["1m", "3m", "5m", "15m", "30m", "1H"]
MANUAL_TFS = ["30m", "1H"]

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

    # ✅ AI SIGNAL (AUTO ONLY)
    direction, ai_confidence = predict_signal(df, symbol, timeframe)

    signal_type = "LONG" if direction == "UP" else "SHORT"
    key = f"{symbol}_{timeframe}"

    # ✅ COOLDOWN
    if key in last_signal_time:
        if time.time() - last_signal_time[key] < 900:
            return

    # ✅ DUPLICATE CHECK
    open_trades = get_open_trades()
    for t in open_trades:
        if t[1] == symbol and t[4] == timeframe:
            print(f"⛔ Duplicate blocked {symbol} {timeframe}")
            return

    last_signal_time[key] = time.time()

    # ===============================
    # ✅ AUTO CONFIDENCE (AI MODEL)
    # ===============================
    auto_confidence = round(ai_confidence, 2)

    if auto_confidence < 70:
        return

    # ===============================
    # ✅ MANUAL CONFIDENCE (VOLATILITY)
    # ===============================
    manual_confidence = min(95, round(volatility * 40, 2))

    # ✅ DEBUG
    print(f"🔍 {symbol} {timeframe} | Vol: {volatility:.2f}% | AI: {auto_confidence}% | Manual: {manual_confidence}%")

    # ✅ TP / SL
    if signal_type == "LONG":
        take_profit = latest * 1.01
        stop_loss = latest * 0.99
    else:
        take_profit = latest * 0.99
        stop_loss = latest * 1.01

    # ✅ CREATE TRADE (AUTO ONLY)
    create_paper_trade(
        symbol,
        signal_type,
        latest,
        1,
        timeframe,
        take_profit,
        stop_loss
    )

    # ✅ QUALITY (AUTO)
    if auto_confidence >= 85:
        quality = "🔥 HIGH"
    elif auto_confidence >= 75:
        quality = "✅ GOOD"
    else:
        quality = "⚠️ WEAK"

    uk_time = get_uk_time().strftime("%H:%M:%S")
    direction_text = "📈 UP" if signal_type == "LONG" else "📉 DOWN"

    # =====================================
    # ✅ AUTO MESSAGE
    # =====================================
    auto_msg = f"""
🤖 AI AUTO SIGNAL

💱 Pair: {symbol}
{direction_text}

💰 Entry: {latest}

🧠 AI Confidence: {auto_confidence}%
🌊 Volatility: {round(volatility, 2)}%
⏱️ TF: {timeframe}
🕒 Time: {uk_time}

🎯 TP: {round(take_profit, 4)}
🛑 SL: {round(stop_loss, 4)}

📊 Quality: {quality}

🚀 Trade executed
"""
    send_message(AUTO_CHAT_ID, auto_msg)

    # ✅ SAVE AUTO
    save_signal(
        table_name,
        symbol,
        signal_type,
        auto_confidence,
        latest,
        "AI",
        volatility,
        trade_source="AUTO"
    )

    # =====================================
    # ✅ MANUAL SIGNAL
    # =====================================
    if timeframe in MANUAL_TFS and volatility >= 0.9:

        # ✅ QUALITY MANUAL
        if manual_confidence >= 85:
            manual_quality = "🔥 STRONG MOVE"
        elif manual_confidence >= 70:
            manual_quality = "✅ GOOD SETUP"
        else:
            manual_quality = "⚠️ LOW MOMENTUM"

        manual_msg = f"""
📡 MANUAL SIGNAL

💱 Pair: {symbol}
{direction_text}
⏱️ TF: {timeframe}

🌊 Volatility: {round(volatility,2)}%
📊 Confidence: {manual_confidence}%

🕒 Time: {uk_time}

📌 Strength: {manual_quality}

⚠️ Manual trade only
"""

        send_message(MANUAL_CHAT_ID, manual_msg)

        # ✅ SAVE MANUAL
        save_signal(
            table_name,
            symbol,
            signal_type,
            manual_confidence,
            latest,
            "VOLATILITY",
            volatility,
            trade_source="MANUAL"
        )

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

            # ✅ TP HIT
            if (side == "LONG" and current >= tp) or (side == "SHORT" and current <= tp):
                print(f"🎯 TP HIT → {pair}")
                close_trade(trade_id, current, round(pnl, 2))

            # ✅ SL HIT
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
            time.sleep(0.2)

        time.sleep(1)
