import mysql.connector
from config import DB_CONFIG
from news_fetcher import update_news
import traceback
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

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:

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

        training_id = cursor.lastrowid  
        conn.commit()
           
        update_news(
                training_id,
                pair
        )

        print(
            f"TRAINING SIGNAL SAVED → {pair} {timeframe}"
        )

    except Exception as e:
            print("========== TRAINING SAVE ERROR ==========")
            traceback.print_exc()
            print("=========================================")

    finally:

        cursor.close()
        conn.close()
