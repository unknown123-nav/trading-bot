import mysql.connector
import traceback

from config import DB_CONFIG
from news_fetcher import update_news

print("HISTORICAL_BUILDER LOADED")


def save_training_signal(
        time,
        uk_time,
        pair,
        timeframe,
        price,
        price_gbp,
        ema20,
        ema50,
        rsi,
        atr,
        natr,
        bb_width,
        chaikin_vol,
        vqi,
        trend_strength,
        channel_position,
        direction,
        confidence,
        power_score,
        financial_strength,
        signal_class,
        market_state,
        frequency_type,
        candle_type
):

    print("SAVE_TRAINING_SIGNAL CALLED")

    conn = None
    cursor = None

    try:

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Connected to database")

        query = """
        INSERT INTO ai_training_dataset(

            time,
            uk_time,

            pair,
            timeframe,

            price,
            price_gbp,

            EMA20,
            EMA50,
            RSI,
            ATR,
            NATR,
            BB_WIDTH,
            CHAIKIN_VOL,
            VQI,
            TREND_STRENGTH,
            CHANNEL_POSITION,

            direction,
            confidence,

            power_score,

            financial_strength,

            signal_class,

            market_state,

            frequency_type,

            candle_type,

            target

        )

        VALUES(

            %s,%s,
            %s,%s,
            %s,%s,

            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,

            %s,%s,

            %s,

            %s,

            %s,

            %s,

            %s,

            %s,

            NULL

        )
        """

        print("Executing INSERT...")

        cursor.execute(
            query,
            (
                time,
                uk_time,

                pair,
                timeframe,

                price,
                price_gbp,

                ema20,
                ema50,
                rsi,
                atr,
                natr,
                bb_width,
                chaikin_vol,
                vqi,
                trend_strength,
                channel_position,

                direction,
                confidence,

                power_score,

                financial_strength,

                signal_class,

                market_state,

                frequency_type,

                candle_type
            )
        )

        print("INSERT OK")

        training_id = cursor.lastrowid

        conn.commit()

        print("COMMIT OK")

        print("Updating news...")

        update_news(
            training_id,
            pair
        )

        print("NEWS UPDATED")

        print(
            f"TRAINING SIGNAL SAVED -> {pair} {timeframe}"
        )

    except Exception:

        print("========== TRAINING SAVE ERROR ==========")
        traceback.print_exc()
        print("=========================================")

    finally:

        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()

        print("Database connection closed")
