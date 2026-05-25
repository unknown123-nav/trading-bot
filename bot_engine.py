from market import get_data
from db import update_bot, save_signal
from config import SYMBOLS
from db import create_paper_trade
from telegram import send_telegram


# =========================================
# PNL CALCULATION
# =========================================

def calculate_pnl(df):

    if len(df) < 2:
        return 0

    return float(
        df.iloc[0]['close']
        - df.iloc[-1]['close']
    )


# =========================================
# AI CONFIDENCE
# =========================================

def calculate_confidence(current, average):

    pct_move = abs(
        (current - average) / average
    ) * 100

    confidence = max(
        50,
        min(
            round(
                50 + (pct_move * 10),
                2
            ),
            99
        )
    )

    return confidence


# =========================================
# GENERIC SIGNAL ENGINE
# =========================================

def process_timeframe(
    symbol,
    timeframe,
    limit,
    table_name
):

    df = get_data(
        symbol,
        timeframe,
        limit
    )

    if df.empty:
        return

    latest = df.iloc[0]['close']

    average = df['close'].mean()

    difference = latest - average

    confidence = calculate_confidence(
        latest,
        average
    )

    signal = (
        "LONG"
        if difference > 0
        else "SHORT"
    )

    print(
        f"{symbol} | {timeframe} | "
        f"{signal} | "
        f"Confidence: {confidence}"
    )

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
    # CREATE PAPER TRADE
    # =====================================

    if confidence >= 75:

        create_paper_trade(
            symbol,
            signal,
            latest,
            confidence,
            timeframe
        )

        message = f"""
🚨 SIGNAL — {symbol}

⏱ Timeframe: {timeframe}

📈 Direction: {signal}

🤖 Confidence: {confidence}%

🎯 Entry: {latest}
"""

        send_telegram(message)


# =========================================
# MAIN BOT ENGINE
# =========================================

def run_bots():

    for symbol in SYMBOLS:

        bot_name = symbol.replace(
            "-USDT",
            " BOT"
        )

        print(f"\nRunning {bot_name}")

        # =====================================
        # 1M
        # =====================================

        process_timeframe(
            symbol,
            "1m",
            60,
            "signals_1m"
        )

        # =====================================
        # 3M
        # =====================================

        process_timeframe(
            symbol,
            "3m",
            40,
            "signals_3m"
        )

        # =====================================
        # 5M
        # =====================================

        process_timeframe(
            symbol,
            "5m",
            40,
            "signals_5m"
        )

        # =====================================
        # 15M
        # =====================================

        process_timeframe(
            symbol,
            "15m",
            40,
            "signals_15m"
        )

        # =====================================
        # 30M
        # =====================================

        process_timeframe(
            symbol,
            "30m",
            40,
            "signals_30m"
        )

        # =====================================
        # 1H
        # =====================================

        process_timeframe(
            symbol,
            "1H",
            40,
            "signals_1h"
        )

        # =====================================
        # BOT STATUS
        # =====================================

        df_status = get_data(
            symbol,
            '1m',
            20
        )

        pnl = calculate_pnl(df_status)

        update_bot(
            bot_name,
            "RUNNING",
            symbol,
            pnl
        )
