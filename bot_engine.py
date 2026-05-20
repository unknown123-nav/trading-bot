from market import get_data
from db import update_bot, save_signal
from config import SYMBOLS
from db import create_paper_trade


def calculate_pnl(df):

    if len(df) < 2:
        return 0

    return float(
        df.iloc[0]['close'] - df.iloc[-1]['close']
    )

# =========================================
# CONFIDENCE CALCULATION
# =========================================

def calculate_confidence(current, average):

    # percentage move
    pct_move = abs(
        (current - average) / average
    ) * 100

    # normalize into cleaner AI-style range
    confidence = max(
        50,
        min(
            round(50 + (pct_move * 10), 2),
            99
        )
    )

    return confidence

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
        # 1M SIGNAL
        # =====================================

        df_1m = get_data(
            symbol,
            '1m',
            60
        )

        if not df_1m.empty:

            latest = df_1m.iloc[0]['close']

            history = df_1m.iloc[3:]['close'].mean()

            difference = latest - history

            confidence = calculate_confidence(
                latest,
                history
            )

            signal = (
                "LONG"
                if difference > 0
                else "SHORT"
            )

            save_signal(
                "signals_1m",
                symbol,
                signal,
                confidence,
                latest
            )

            if confidence >= 40:
                create_paper_trade(symbol, signal, latest, confidence, "1m")
        # =====================================
        # 3M SIGNAL
        # =====================================

        df_3m = get_data(
            symbol,
            '3m',
            20
        )

        if not df_3m.empty:

            latest = df_3m.iloc[0]['close']

            history = df_3m.iloc[2:]['close'].mean()

            difference = latest - history

            confidence = calculate_confidence(
                latest,
                history
            )

            signal = (
                "LONG"
                if difference > 0
                else "SHORT"
            )

            save_signal(
                "signals_3m",
                symbol,
                signal,
                confidence,
                latest
            )
            if confidence >= 40:
                create_paper_trade(symbol, signal, latest, confidence, "1m")

        # =====================================
        # 30M SIGNAL
        # =====================================

        df_30m = get_data(
            symbol,
            '30m',
            20
        )

        if not df_30m.empty:

            latest = df_30m.iloc[0]['close']

            avg = df_30m['close'].mean()

            difference = latest - avg

            confidence = calculate_confidence(
                latest,
                avg
            )

            signal = (
                "LONG"
                if difference > 0
                else "SHORT"
            )

            save_signal(
                "signals_30m",
                symbol,
                signal,
                confidence,
                latest
            )
            if confidence >= 40:
                create_paper_trade(symbol, signal, latest, confidence, "1m")

        # =====================================
        # BOT STATUS
        # =====================================

        pnl = calculate_pnl(
            df_1m
            if not df_1m.empty
            else df_30m
        )

        update_bot(
            bot_name,
            "RUNNING",
            symbol,
            pnl
        )