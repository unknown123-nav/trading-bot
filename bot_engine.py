import time
import requests
from market import get_data
from db import update_bot, save_signal
from config import SYMBOLS
from db import create_paper_trade
from db import get_open_trades
from db import close_trade
from ai_engine import predict_trade

# ✅ SIGNAL BOT FUNCTION
def send_signal(message):
    token = "8864549600:AAH8S3USLHU6mOHSbcfxsMdrjYn47TXGCBY"
    chat_id = "-5211298112"

    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message}
        )
        print("✅ Signal sent")
    except Exception as e:
        print("Signal error:", e)


# ✅ CONFIDENCE
def calculate_confidence(current, average):
    pct = abs((current - average) / average) * 100
    return max(50, min(round(50 + (pct * 10), 2), 99))


# ✅ PROCESS SIGNAL
def process_timeframe(symbol, timeframe, table_name):

    df = get_data(symbol, timeframe, 40)

    if df.empty:
        return

    latest = float(df.iloc[0]['close'])

    avg = float(df['close'].mean())

    signal =
        "LONG" if latest > avg else "SHORT"

    confidence =
        calculate_confidence(
            latest,
            avg
        )

    # =====================================
    # AI FEATURES
    # =====================================

    delta =
        abs(latest - avg)

    percentile =
        confidence

    pnl = 0

    # =====================================
    # AI PREDICTION
    # =====================================

    ai_probability =
        predict_trade(
            symbol,
            timeframe,
            signal,
            confidence,
            delta,
            percentile,
            pnl
        )

    print(
        f"🧠 AI Probability: {ai_probability}"
    )

    # =====================================
    # AI FILTER
    # =====================================

    if ai_probability < 0.70:

        print(
            f"❌ AI rejected {symbol} {timeframe}"
        )

        return

    # =====================================
    # SAVE SIGNAL
    # =====================================

    save_signal(
        table_name,
        symbol,
        signal,
        confidence,
        latest
    )

    # =====================================
    # CREATE TRADE
    # =====================================

    if confidence >= 55:

        create_paper_trade(
            symbol,
            signal,
            latest,
            confidence,
            timeframe
        )

        message = f"""
🚨 AI SIGNAL

{symbol} {timeframe}

{signal}

Confidence: {confidence}%

AI Probability:
{round(ai_probability * 100, 2)}%

Entry: {latest}

Time:
{time.strftime('%Y-%m-%d %H:%M:%S')}
"""

        send_signal(message)

# ✅ MONITOR TRADES (IMPORTANT — THIS WAS REQUIRED)
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

        pnl = ((current - entry) / entry * 100) if side == "LONG" else ((entry - current) / entry * 100)
        pnl = round(pnl, 2)

        if pnl >= 2 or pnl <= -1:

            close_trade(trade_id, current, pnl)

            message = f"""
✅ TRADE CLOSED

{pair}
{side}
PNL: {pnl}%

Time: {time.strftime('%H:%M:%S')}
"""

            send_signal(message)


# ✅ MAIN BOT FUNCTION (THIS FIXES YOUR ERROR)
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
