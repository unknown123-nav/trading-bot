from db import get_connection

def save_historical_signal(
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
    candle_type
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
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
        %s,%s,%s,%s,%s,%s,
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
        %s,%s,%s,%s,%s,%s,%s,%s,
        NULL
        )

        """,

        (

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

        candle_type

        ))

        conn.commit()

        print("Historical row saved")

    except Exception as e:

        print("Historical error:",e)

    finally:

        cursor.close()
        conn.close()
