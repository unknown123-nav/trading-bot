import time
import requests
from market import get_data
from db import update_bot, save_signal
from config import SYMBOLS
from db import create_paper_trade
from db import get_open_trades
from db import close_trade


# =========================================
#  SIGNAL BOT (SEPARATE BOT)
# =========================================
def send_signal(message):
    token = "8864549600:AAH8S3USLHU6mOHSbcfxsMdrjYn47TXGCBY"   
    chat_id = "-5211298112"

    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": message
            }
        )
        print("✅ Signal sent")
    except Exception as e:
        print("Signal bot error:", e)


# =========================================
# PNL CALCULATION
# =========================================
def calculate_pnl(df):
    if len(df) < 2:
        return 0

    return float(
        df.iloc[0]['close'] -
        df.iloc[-1]['close']
    )


# =========================================
# AI CONFIDENCE
# =========================================
def calculate_confidence(current, average):

    pct_move = abs(
        (current - average) / average
    ) * 100

    return max(
        50,
        min(round(50 + (pct_move * 10), 2), 99)
    )


# =========================================
# GENERIC SIGNAL ENGINE
# =========================================
def process_timeframe(symbol, timeframe, limit, table_name):

    df = get_data(symbol, timeframe, limit)

    if df.empty:
        return

    latest = df.iloc[0]['close']
    average = df['close'].mean()

    confidence = calculate_confidence(latest, average)

    signal = "LONG" if latest > average else "SHORT"

    print(f"{symbol} | {timeframe} | {signal} | Confidence: {confidence}")

    save_signal(table_name, symbol, signal, confidence, latest)

    # =====================================
    # MARKET STATE
    # =====================================
    if confidence < 55:
        market_state = "LOW VOLATILITY"
        ai_analysis = "Weak momentum"
        risk_reward = "1 : 1"
    elif confidence < 70:
        market_state = "BUILDING MOMENTUM"
        ai_analysis = "Moderate build-up"
        risk_reward = "1 : 1.5"
    elif confidence < 85:
        market_state = "HIGH VOLATILITY"
        ai_analysis = "Strong movement"
        risk_reward = "1 : 2"
    else:
        market_state = "BREAKOUT"
        ai_analysis = "Aggressive momentum"
        risk_reward = "1 : 3"

    # =====================================
    # TP / SL
    # =====================================
    take_profit = round(latest * 1.02, 4)
    stop_loss = round(latest * 0.985, 4)

    print(f"Confidence Check: {confidence}")

    if confidence >= 55:

        create_paper_trade(symbol, signal, latest, confidence, timeframe)

        # ✅ SIGNAL MESSAGE (USES SIGNAL BOT)
        message = f"""
🚨 KRYPTRA SIGNAL

{symbol} | {timeframe}

Direction: {signal}
Confidence: {confidence}%

Entry: {latest}
TP: {take_profit}
SL: {stop_loss}

Market: {market_state}
RR: {risk_reward}

Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}
"""

        send_signal(message)


# =========================================
# TRADE MONITOR ENGINE
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

        current_price = float(df.iloc[0]['close'])

        pnl = (
            (current_price - entry) / entry * 100
            if side == "LONG"
            else (entry - current_price) / entry * 100
        )

        pnl = round(pnl, 2)

        if pnl >= 2 or pnl <= -1:

            close_trade(trade_id, current_price, pnl)

            result = "TAKE PROFIT ✅" if pnl > 0 else "STOP LOSS ❌"

            message = f"""
✅ TRADE CLOSED — {pair}

{side}
Entry: {entry}
Exit: {current_price}
PNL: {pnl}%

{result}
{time.strftime('%Y-%m-%d %H:%M:%S UTC')}
"""

            send_signal(message)

