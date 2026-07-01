import mysql.connector
import traceback

from config import DB_CONFIG

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
        candle_type,
        trigger_headline,
        trigger_summary,
        trigger_source,
        trigger_news_score,
        minutes_before_breakout,
        trigger_label
):

    print("SAVE_TRAINING_SIGNAL CALLED")

    conn = None
    cursor = None

    try:

        pair = str(pair)
        timeframe = str(timeframe)

        price = float(price)
        price_gbp = float(price_gbp)

        ema20 = float(ema20)
        ema50 = float(ema50)
        rsi = float(rsi)
        atr = float(atr)
        natr = float(natr)

        bb_width = float(bb_width)
        chaikin_vol = float(chaikin_vol)
        vqi = float(vqi)

        trend_strength = float(trend_strength)
        channel_position = float(channel_position)

        direction = str(direction)

        confidence = float(confidence)

        power_score = float(power_score)

        financial_strength = float(financial_strength)

        signal_class = str(signal_class)

        market_state = int(market_state)

        frequency_type = int(frequency_type)

        candle_type = str(candle_type)

        trigger_headline = str(trigger_headline or "")
        trigger_summary = str(trigger_summary or "")
        trigger_source = str(trigger_source or "")
        trigger_news_score = float(trigger_news_score or 0)
        minutes_before_breakout = float(minutes_before_breakout or 0)
        if trigger_label is None:
                trigger_label = None
        else:
                trigger_label = int(trigger_label)

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
            trigger_headline,
            trigger_summary,
            trigger_source,
            trigger_news_score,
            minutes_before_breakout,
            trigger_label,
            breakout_strength,
            breakout_direction,
            move_percent,
            expansion,

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
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,

            NULL

        )
        """

        values = (

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

            candle_type,
            trigger_headline,
            trigger_summary,
            trigger_source,
            trigger_news_score,
            minutes_before_breakout,
            trigger_label
        )

        print("Executing INSERT...")

        cursor.execute(query, values)

        print("INSERT OK")

        training_id = cursor.lastrowid

        conn.commit()

        print("COMMIT OK")

        print("Updating news...")

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
