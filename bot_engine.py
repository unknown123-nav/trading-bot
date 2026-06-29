print("1")
import time

print("2")
import requests

print("3")
from datetime import datetime

print("4")
import pytz

print("5")
from trend_classifier import classify_market

print("6")
from volatility_indicators import *

print("7")
from market import get_data

print("8")
from db import (
    create_paper_trade,
    get_open_trades,
    close_trade,
    save_signal,
    save_telegram_log
)

print("9")
from config import SYMBOLS

print("10")
from ai_engine import predict_signal

print("11")
from historical_builder import save_training_signal

print("12")
from outcome_tracker import update_targets

print("13")
from manual_ai_engine import safe_predict_manual_trade

print("14")
from breakout_detector import detect_breakout
from news_fetcher import fetch_news

print("BOT ENGINE IMPORT COMPLETE")
processing = {}

recent_symbols = {}

last_signal_time = {}

roi_state = {}

roi_last_signal = {}

roi_last_price = {}

roi_enter_time = {}
roi_confirmation = {}

TELEGRAM_TOKEN = "8626450626:AAGooyT7nO1kLxdOe4KbzV20JqJye7JVcio"
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
        if market_type == "SIDEWAYS":
            print(f"SKIPPED {symbol} {timeframe} → SIDEWAYS MARKET")
            return
            
        if volatility_type == "LOW" and timeframe in ["1m","3m","5m"]:
            print(
                f"SKIPPED {symbol} {timeframe}"
                " → LOW VOLATILITY"
            )
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

        
        if direction == "UP" and latest < ema20:
            print(
                f"SKIPPED {symbol} {timeframe}"
                " → EMA FILTER FAILED"
            )
            return
            
        if direction == "DOWN" and latest > ema20:
            print(
                f"SKIPPED {symbol} {timeframe}"
                " → EMA FILTER FAILED"
            )
            return

        if direction == "UP" and latest > bb_upper:
            print(
                f"SKIPPED {symbol} {timeframe}"
                " → OVERBOUGHT"
            )
            return
            
        if direction == "DOWN" and latest < bb_lower:
            print(
                f"SKIPPED {symbol} {timeframe}"
                " → OVERSOLD"
            )
            return
        sma10 = df['close'].head(10).mean()
        sma30 = df['close'].head(30).mean()

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
            print(
                f"SKIPPED {symbol} {timeframe} → INVALID CHANNEL"
            )
            return
        channel_position = (
            latest - lower_line
        ) / channel_range
        if direction == "UP" and channel_position > 0.80:
            print(
                f"SKIPPED {symbol} {timeframe}"
                f" → LONG TOO HIGH ({channel_position:.2f})"
            )
            return
            
        if direction == "DOWN" and channel_position < 0.20:
            print(
                f"SKIPPED {symbol} {timeframe}"
                f" → SHORT TOO LOW ({channel_position:.2f})"
            )
            return
        
        candle_type = detect_candle_pattern(df)
        print(f" {symbol} {timeframe} → AI: {round(ai_confidence,2)} | Vol: {round(volatility,2)}")
        if ai_confidence < 75 or volatility < 1:
            reason = []
            if ai_confidence < 75:
                print(
                    f"SKIPPED {symbol} {timeframe} → LOW AI "
                    f"| AI={ai_confidence:.2f}"
                )
                return
                
            if volatility < 1:
                reason.append(f"VOL LOW ({round(volatility,2)}%)")
                
            print(f" SKIPPED → {symbol} {timeframe} | {' & '.join(reason)}")
            return

        #  GLOBAL LIMIT
        symbol_key = f"{symbol}_global"
        if symbol_key in recent_symbols:
            if time.time() - recent_symbols[symbol_key] < 150:
                return

        signal_type = "LONG" if direction == "UP" else "SHORT"
        direction_text = "UP" if signal_type == "LONG" else "DOWN"
        unstable, ratio = atr_instability(df)
        upper_dc, lower_dc, width = donchian_channel(df)
        if width / latest * 100 > 8:
            print(
                f"SKIPPED {symbol} {timeframe}"
                f" → DONCHIAN SPIKE"
            )
            return
        
        if unstable and ratio > 1.8:
            print(
                f"SKIPPED {symbol} {timeframe}"
                f" → ATR SPIKE ({ratio:.2f})"
            )
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

        save_signal(table_name, symbol, signal_type, confidence, latest,candle_type, volatility, trade_source="AUTO")

        save_telegram_log(message_text, "AUTO_CHANNEL", "SENT")

    except Exception as e:
        print(f" AUTO ERROR → {symbol} {timeframe}: {e}")
        time.sleep(1)


    finally:
        processing[key] = False

# =========================================
# MANUAL AI (30m / 1H)
# =========================================
def process_manual(symbol, timeframe, table_name):

    if timeframe not in MANUAL_TFS:
        return

    try:

        df = get_data(symbol, timeframe, 40)

        if timeframe == "30m":
            if not detect_breakout(df):
                print(
                    f"{symbol} 30m -> No breakout"
                )
                return
                breakout_time = get_uk_time()
                print(
                    f"BREAKOUT AT {breakout_time}"
                )
            print(
                f"{symbol} 30m -> BREAKOUT DETECTED"
            )

        if timeframe == "1H":
            if not detect_breakout(df):
                print(
                    f"{symbol} 1H -> No breakout"
                )
                return
                breakout_time = get_uk_time()
                print(
                    f"BREAKOUT AT {breakout_time}"
                )
            print(
                f"{symbol} 1H -> BREAKOUT DETECTED"
            )

        if df.empty:
            return

        latest = float(df.iloc[0]["close"])

        GBP_RATE = 0.74
        gbp_price = latest * GBP_RATE

        # ==============================
        # PREVENT SPAM
        # ==============================

        key = f"{symbol}_{timeframe}_MANUAL"

        if key in last_signal_time:
            if time.time() - last_signal_time[key] < 1800:
                return

        # ==============================
        # NEWS
        # ==============================

        articles = fetch_news(symbol)

        if articles:

            news = {
                "headline": articles[0].get("title", ""),
                "summary": articles[0].get("summary", "")
            }

        else:

            news = None

        # ==============================
        # MANUAL AI
        # ==============================

        ai_result = safe_predict_manual_trade(
            df=df,
            pair=symbol,
            timeframe=timeframe,
            news=news
        )

        if ai_result["roi_score"] < 80:
            print(
                f"ROI rejected ({ai_result['roi_score']})"
            )
            return
        if ai_result is None:
            return

        roi_key = f"{symbol}_{timeframe}"
        if roi_state.get(roi_key, False):
            exit_message = f"""
            ROI EXIT
            Pair : {symbol}
            Timeframe : {timeframe}
            The market is no longer inside the region of interest.
            """
            send_message(
                MANUAL_CHAT_ID,
                exit_message
    
            )
            save_telegram_log(
        
                exit_message,
        
                "MANUAL_CHANNEL",
        
                "SENT"
    
            )
            roi_state[roi_key] = False
            roi_confirmation[roi_key] = 0
            roi_last_signal.pop(roi_key, None)
            roi_last_price.pop(roi_key, None)
            roi_enter_time.pop(roi_key, None)
            print(f"ROI ENDED -> {symbol} {timeframe}")

        
        if ai_result["signal"] == "NO TRADE":
            print(f"MANUAL AI -> NO TRADE | {symbol} {timeframe}")
            save_training_signal(
                time=df.iloc[0]["time"],
                uk_time=get_uk_time(),
                pair=symbol,
                timeframe=timeframe,
                price=latest,
                price_gbp=gbp_price,
                ema20=float(df.iloc[0]["EMA20"]),
                ema50=float(df.iloc[0]["EMA50"]),
                rsi=float(df.iloc[0]["RSI"]),
                atr=float(df.iloc[0]["ATR"]),
                natr=float(df.iloc[0]["NATR"]),
                bb_width=float(df.iloc[0]["BB_WIDTH"]),
                chaikin_vol=float(df.iloc[0]["CHAIKIN_VOL"]),
                vqi=float(df.iloc[0]["VQI"]),
                trend_strength=float(df.iloc[0]["TREND_STRENGTH"]),
                channel_position=float(df.iloc[0]["CHANNEL_POSITION"]),
                direction="NONE",
                confidence=ai_result["confidence"],
                power_score=ai_result["power_score"],
                financial_strength=ai_result["financial_strength"],
                signal_class="NO TRADE",
                market_state=ai_result["market_state"],
                frequency_type=ai_result["frequency_type"],
                candle_type=ai_result["candle_type"]
            )
            return

        # ==============================
        # AI OUTPUT
        # ==============================

        direction = (
            "UP"
            if ai_result["signal"] == "BUY"
            else "DOWN"
        )

        signal_type = (
            "LONG"
            if direction == "UP"
            else "SHORT"
        )

        roi_key = f"{symbol}_{timeframe}"
        current_signal = ai_result["signal"]
        previous_signal = roi_last_signal.get(roi_key)
        inside_roi = roi_state.get(roi_key, False)
        confirmation = roi_confirmation.get(roi_key, 0)
        confidence = ai_result["confidence"]

        candle_type = ai_result["candle_type"]

        power_score = ai_result["power_score"]

        financial_strength = ai_result["financial_strength"]

        market_state = ai_result["market_state"]

        frequency_type = ai_result["frequency_type"]

        volatility = float(df.iloc[0]["NATR"])

        uk_time=get_uk_time(),

        last_signal_time[key] = time.time()

        # ==============================
        # TELEGRAM
        # ==============================

        message = f"""
📡 MANUAL AI SIGNAL

Pair : {symbol}

Direction : {direction}

Signal : {ai_result['signal']}

Confidence : {confidence}%

Strength : {ai_result['strength']}

Probability : {round(ai_result['probability'],4)}

Power Score : {power_score}

Financial Strength : {financial_strength}

Market State : {market_state}

Frequency : {frequency_type}

Candle : {candle_type}

Timeframe : {timeframe}

Time : {uk_time}
"""

        if not inside_roi:
            if current_signal == previous_signal:
                confirmation += 1

             else:
                 confirmation = 1
                
             roi_confirmation[roi_key] = confirmation
             print(
                 f"{symbol} {timeframe} ROI Confirmation {confirmation}/3"
             )
            if confirmation >= 3:
                roi_score = 0
                
            if trend_strength > 0.80:
                roi_score += 20
                
            if power_score >= 60:
                roi_score += 20
                
            if financial_strength >= 40:
                roi_score += 20
                
            if ai_result["interesting_signal"]:
                roi_score += 20
                
            if confidence >= 90:
                roi_score += 20
                
            print(f"ROI Score : {roi_score}")
            
            if roi_score < 80:
                print(
                    f"ROI rejected -> Score {roi_score}"
                )
                roi_confirmation[roi_key] = 0
                return
                send_message(
                
                    MANUAL_CHAT_ID,
                
                    message
            
                )
                save_telegram_log(
                
                    message,
                
                    "MANUAL_CHANNEL",
                
                    "SENT"
            
                )
            roi_state[roi_key] = True
            roi_last_signal[roi_key] = current_signal
            roi_last_price[roi_key] = latest
            roi_enter_time[roi_key] = time.time()
            roi_confirmation[roi_key] = 0
            print(f"ROI STARTED -> {symbol} {timeframe}")
        else:
            print(f"ROI ACTIVE -> {symbol} {timeframe} (No Telegram)")

        # ==============================
        # SAVE SIGNAL
        # ==============================

        save_signal(
            table_name,
            symbol,
            signal_type,
            confidence,
            latest,
            candle_type,
            volatility,
            trade_source="MANUAL"
        )

        # ==============================
        # SAVE TRAINING DATASET
        # ==============================

        save_training_signal(

            time=df.iloc[0]["time"],

            uk_time=get_uk_time(),

            pair=symbol,

            timeframe=timeframe,

            price=latest,

            price_gbp=gbp_price,

            ema20=float(df.iloc[0]["EMA20"]),

            ema50=float(df.iloc[0]["EMA50"]),

            rsi=float(df.iloc[0]["RSI"]),

            atr=float(df.iloc[0]["ATR"]),

            natr=float(df.iloc[0]["NATR"]),

            bb_width=float(df.iloc[0]["BB_WIDTH"]),

            chaikin_vol=float(df.iloc[0]["CHAIKIN_VOL"]),

            vqi=float(df.iloc[0]["VQI"]),

            trend_strength=float(df.iloc[0]["TREND_STRENGTH"]),

            channel_position=float(df.iloc[0]["CHANNEL_POSITION"]),

            direction=direction,

            confidence=confidence,

            power_score=power_score,

            financial_strength=financial_strength,

            signal_class=ai_result["signal"],

            market_state=market_state,

            frequency_type=frequency_type,

            candle_type=candle_type

        )
        print("Returned from save_training_signal()")

        print(
            f"MANUAL AI SIGNAL SAVED -> {symbol} {timeframe}"
        )

    except Exception as e:

        print(
            f"MANUAL ERROR -> {symbol} {timeframe}: {e}"
        )
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

    print("BOT RUNNING")

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
        update_targets()

        time.sleep(3)
