import time
import requests
from datetime import datetime
import pytz
from trend_classifier import classify_market
from volatility_indicators import *
from market import get_data
from db import create_paper_trade, get_open_trades, close_trade, save_signal, save_telegram_log
from config import SYMBOLS
from ai_engine import predict_signal

print("bot_engine LOADED")
processing = {}
recent_symbols = {}
last_signal_time = {}

TELEGRAM_TOKEN = "8625282562:AAGNQZgdVK0mPYrXJ2GOAlc55HW74_5glak"
AUTO_CHAT_ID = "-5211298112"
MANUAL_CHAT_ID = "-5287950499"

MANUAL_TFS = ["30m", "1H"]

def get_uk_time():
    return datetime.now(pytz.timezone("Europe/London"))

def detect_candle_pattern(df):
    open_price = df.iloc[0]['open']
    close_price = df.iloc[0]['close']
    high = df.iloc[0]['high']
    low = df.iloc[0]['low']

    body = abs(close_price - open_price)
    range_ = high - low

    if range_ == 0:
        return "Flat"

    # Doji
    if body <= (range_ * 0.1):
        return "Doji"

    # Bullish / Bearish Engulfing (basic)
    if len(df) > 1:
        prev_open = df.iloc[1]['open']
        prev_close = df.iloc[1]['close']

        # Bullish engulfing
        if close_price > open_price and prev_close < prev_open:
            return "Bullish Engulfing"

        # Bearish engulfing
        if close_price < open_price and prev_close > prev_open:
            return "Bearish Engulfing"

    # Basic trend candle
    if close_price > open_price:
        return "Bullish Candle"
    else:
        return "Bearish Candle"
        
# TELEGRAM
def send_message(chat_id, message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": message}
        )
    except:
        print(" Telegram failed")

# =========================================
#  AUTO (REAL TRADES ONLY)
# =========================================
def process_auto(symbol, timeframe, table_name):

    key = f"{symbol}-{timeframe}"

    if processing.get(key):
        return

    processing[key] = True

    try:
        print(f"Checking → {symbol} {timeframe}")
        df = get_data(symbol, timeframe, 40)
        if df.empty:
            print(f" NO DATA → {symbol} {timeframe}")
            return

        latest = float(df.iloc[0]['close'])
        GBP_RATE = 0.74
        gbp_price = latest * GBP_RATE
        
        avg = float(df['close'].mean())
        volatility = abs(latest - avg) / avg * 100
        
        direction, ai_confidence = predict_signal(df, symbol, timeframe)
        market_type = classify_market(df)
        volatility_type = volatility_regime(df)
        print(
            f"{symbol} {timeframe} | "
            f"{market_type} | "
            f"{volatility_type}"
        )
        if market_type in ["RANGING", "SIDEWAYS"]:
            print("SIDEWAYS MARKET")
            return
            
        if volatility_type == "LOW":
            print("LOW VOLATILITY")
            return
        atr = float(df.iloc[0]["ATR"])
        rsi = float(df.iloc[0]["RSI"])
        if direction == "UP" and rsi > 75:
            print("RSI OVERBOUGHT")
            return
            
        if direction == "DOWN" and rsi < 25:
            print("RSI OVERSOLD")
            return
        ema20 = float(df.iloc[0]["EMA20"])
        bb_upper = float(df.iloc[0]["BB_UPPER"])
        bb_lower = float(df.iloc[0]["BB_LOWER"])

        adx = float(df.iloc[0]["ADX"])
        if adx < 20:
            print("WEAK TREND")
            return
        
        if direction == "UP" and latest < ema20:
            print("EMA FILTER FAILED")
            return
            
        if direction == "DOWN" and latest > ema20:
            print("EMA FILTER FAILED")
            return

        if direction == "UP" and latest > bb_upper:
            print("OVERBOUGHT")
            return
            
        if direction == "DOWN" and latest < bb_lower:
            print("OVERSOLD")
            return
        sma10 = df['close'].head(10).mean()
        sma30 = df['close'].head(30).mean()

        macd = float(df.iloc[0]["MACD"])
        
        macd_signal = float(df.iloc[0]["MACD_SIGNAL"])
        if direction == "UP" and macd < macd_signal:
            print("MACD FILTER FAILED")
            return
            
        if direction == "DOWN" and macd > macd_signal:
            print("MACD FILTER FAILED")
            return
        trend_strength = abs(
            sma10 - sma30
        ) / sma30 * 100
        if trend_strength < 0.30:
            print(
                f"FLAT MARKET → {symbol} {timeframe}"
            )
            return
        upper_line = (
            df['high']
            .head(20)
            .rolling(5)
            .mean()
            .dropna()
            .iloc[-1]
        )
        lower_line = (
            df['low']
            .head(20)
            .rolling(5)
            .mean()
            .dropna()
            .iloc[-1]
        )
        channel_range = upper_line - lower_line
        if channel_range <= 0:
            return
        channel_position = (
            latest - lower_line
        ) / channel_range
        if direction == "UP" and channel_position > 0.30:
            print(
                f"ROI FAILED LONG → {symbol} {timeframe}"
            )
            return
            
        if direction == "DOWN" and channel_position < 0.70:
            print(
                f"ROI FAILED SHORT → {symbol} {timeframe}"
            )
            return

        
        candle_type = detect_candle_pattern(df)
        print(f" {symbol} {timeframe} → AI: {round(ai_confidence,2)} | Vol: {round(volatility,2)}")
        if ai_confidence < 85 or volatility < 3:
            reason = []
            if ai_confidence < 85:
                reason.append(f"AI LOW ({round(ai_confidence,2)})")
                
            if volatility < 3:
                reason.append(f"VOL LOW ({round(volatility,2)}%)")
                
            print(f" SKIPPED → {symbol} {timeframe} | {' & '.join(reason)}")
            return

        #  GLOBAL LIMIT
        symbol_key = f"{symbol}_global"
        if symbol_key in recent_symbols:
            if time.time() - recent_symbols[symbol_key] < 300:
                return

        signal_type = "LONG" if direction == "UP" else "SHORT"
        direction_text = "UP" if signal_type == "LONG" else "DOWN"
        unstable, ratio = atr_instability(df)
        upper_dc, lower_dc, width = donchian_channel(df)
        if width / latest * 100 > 5:
            print("DONCHIAN VOLATILITY SPIKE")
            return
        
        if unstable and ratio > 1.8:
            print("ATR VOLATILITY SPIKE")
            return
        open_trades = get_open_trades()
        for t in open_trades:
            if t[1] == symbol and t[2] == signal_type:
                print(f" ALREADY OPEN → {symbol} {signal_type}")
                return

        confidence = (
            ai_confidence * 0.85
            + volatility * 5
        )
        confidence = min(round(confidence, 2), 99)


        if signal_type == "LONG":
            tp = latest + (2 * atr)
            sl = latest - atr
        else:
            tp = latest - (2 * atr)
            sl = latest + atr

        created = create_paper_trade(symbol, signal_type, latest, 1, timeframe, tp, sl)

        if not created:
            print(f" BLOCKED → {symbol} {timeframe}")
            return

        recent_symbols[symbol_key] = time.time()

        print(f" REAL TRADE → {symbol} {timeframe}")

        uk_time = get_uk_time().strftime("%H:%M:%S")

        tp_gbp = tp * GBP_RATE
        sl_gbp = sl * GBP_RATE

        message_text = f"""
🤖 AUTO TRADE STARTED

Pair: {symbol}
Direction: {direction_text}
candle_type: {candle_type}
Market: {market_type}
Volatility Regime: {volatility_type}
Entry: £{round(gbp_price, 2)} ({latest} USDT)

Confidence: {confidence}%
Volatility: {round(volatility,2)}%
Timeframe: {timeframe}
Time: {uk_time}

TP: £{round(tp_gbp, 2)}
SL: £{round(sl_gbp, 2)}
"""

        send_message(AUTO_CHAT_ID, message_text)

        save_signal(table_name, symbol, signal_type, confidence, latest,candle_type, "AI", volatility, trade_source="AUTO")

        save_telegram_log(message_text, "AUTO_CHANNEL", "SENT")

    except Exception as e:
        print(f" AUTO ERROR → {symbol} {timeframe}: {e}")
        time.sleep(1)


    finally:
        processing[key] = False
# =========================================
#  MANUAL (NO TRADES)
# =========================================
def process_manual(symbol, timeframe, table_name):

    if timeframe not in MANUAL_TFS:
        return

    df = get_data(symbol, timeframe, 40)
    if df.empty:
        return

    latest = float(df.iloc[0]['close'])
    candle_type = detect_candle_pattern(df)

    GBP_RATE = 0.74  
    gbp_price = latest * GBP_RATE
    avg = float(df['close'].mean())
    volatility = abs(latest - avg) / avg * 100

    direction = "UP" if latest > avg else "DOWN"
    if volatility < 5.6 :
        print(f" MANUAL SKIP → {symbol} {timeframe} | Vol: {round(volatility,2)}")
        return

    confidence = round(min(95, 50 + (volatility * 10)), 2)

    key = f"{symbol}_{timeframe}_MANUAL"
    if key in last_signal_time:
        if time.time() - last_signal_time[key] < 300:
            return

    last_signal_time[key] = time.time()

    direction_text = direction
    signal_type = "LONG" if direction == "UP" else "SHORT"
    
    uk_time = get_uk_time().strftime("%H:%M:%S")

    message_text = f"""
📡 MANUAL SIGNAL

Pair: {symbol}
Direction: {direction_text}
candle_type: {candle_type}
Timeframe: {timeframe}

Volatility: {round(volatility,2)}%
Confidence: {confidence}%
Time: {uk_time}
"""

    send_message(MANUAL_CHAT_ID, message_text)

    save_signal(table_name, symbol, signal_type, confidence, latest,candle_type, volatility, trade_source="MANUAL")

    save_telegram_log(message_text, "MANUAL_CHANNEL", "SENT")


# =========================================
#  MONITOR TRADES
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

            GBP_RATE = 0.74
            entry_gbp = entry * GBP_RATE
            exit_gbp = current * GBP_RATE

            pnl = (
                (current - entry) / entry * 100
                if side == "LONG"
                else (entry - current) / entry * 100
            )

            should_close = False

            if (side == "LONG" and current >= tp) or (side == "SHORT" and current <= tp):
                print(f"TP HIT → {pair}")
                should_close = True

            elif (side == "LONG" and current <= sl) or (side == "SHORT" and current >= sl):
                print(f"SL HIT → {pair}")
                should_close = True

            if should_close:
                conn = None
                try:
                    from db import get_connection
                    conn = get_connection()
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT status FROM paper_trades WHERE id = %s",
                        (trade_id,)
                    )
                    status = cursor.fetchone()

                    if not status or status[0] != "OPEN":
                        continue

                finally:
                    if conn:
                        conn.close()

                # CORRECT BLOCK
                result = "WIN" if pnl > 0 else "LOSS"
                uk_time = get_uk_time().strftime("%H:%M:%S")

                message_text = f"""TRADE CLOSED

Pair: {pair}
Side: {side}

Entry: £{round(entry_gbp, 2)}
Exit: £{round(exit_gbp, 2)}

PnL: {round(pnl, 2)}%
Result: {result}

Time: {uk_time}
"""

                print("Sending close message...")  
                send_message(AUTO_CHAT_ID, message_text)

                save_telegram_log(message_text, "AUTO_CHANNEL", "CLOSED")
                close_trade(trade_id, current, round(pnl, 2))

        except Exception as e:
            print("Monitor error:", e)
# =========================================
#  RUN BOT
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
                time.sleep(0.5)

        monitor_trades()

        time.sleep(3)
