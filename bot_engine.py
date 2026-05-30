import time
import requests

from market import get_data
from db import (
    update_bot,
    save_signal,
    create_paper_trade,
    get_open_trades,
    close_trade
)
from config import SYMBOLS
from ai_engine import predict_trade

daily_signals_count = 0
last_reset_day = time.strftime("%Y-%m-%d")
last_run_time = time.time()

# =========================================
# ✅ TELEGRAM SIGNAL
# =========================================
def send_signal(message):
    token = "8864549600:AAHaY2Q84VpkDBhYH6J0X4SNzpj-DLvGM_k"
    chat_id = "-5211298112"

    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=3
        )
    except Exception as e:
        print("Signal error:", e)
import time
import requests

from market import get_data
from db import (
    create_paper_trade,
    get_open_trades,
    close_trade
)
from config import SYMBOLS

# ✅ GLOBALS
daily_signals_count = 0
last_reset_day = time.strftime("%Y-%m-%d")


# =========================================
# ✅ TELEGRAM
# =========================================
def send_signal(message):
    token = "YOUR_TOKEN"
    chat_id = "YOUR_CHAT_ID"

    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=3
        )
    except Exception as e:
        print("Signal error:", e)


# =========================================
# ✅ PROCESS SIGNAL
# =========================================
def process_timeframe(symbol, timeframe):

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

    # ✅ SIMPLE FILTER
    volatility = abs(latest - avg) / avg * 100

    if volatility < 0.5:
        return

    # ✅ CHECK EXISTING TRADES
    open_trades = get_open_trades()

    for t in open_trades:
        if t[1] == symbol:
            return

    # ✅ CREATE TRADE
    create_paper_trade(symbol, signal_type, latest, 0, timeframe)

    # ✅ FORMAT MESSAGE (TEACHER STYLE)
    direction = "UP" if signal_type == "LONG" else "DOWN"

    send_signal(f"""
📊 TRADE SIGNAL

Pair: {symbol}
Direction: {direction}
Entry: {latest}
Volatility: {round(volatility, 2)}%


Timeframe: {timeframe}
Date: {time.strftime('%d-%m-%Y')}
Time: {time.strftime('%H:%M:%S')}
""")

    daily_signals_count += 1


# =========================================
# ✅ MONITOR TRADES (ONLY CLOSE)
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

        except:
            continue


# =========================================
# ✅ RUN BOT
# =========================================
def run_bot():
    print("💓 BOT RUNNING")

    for tf, table in [
                ("5m", "signals_5m"),
                ("15m", "signals_15m")
            ]:
                 process_timeframe(symbol, tf, table)

        except Exception as e:
            print("Error:", e)

        time.sleep(5)


# =========================================
# ✅ MAIN LOOP
# =========================================
while True:
    run_bot()
    monitor_trades()
    time.sleep(300)   # ✅ every 5 minutes
