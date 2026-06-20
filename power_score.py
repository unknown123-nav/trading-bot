def calculate_power_score(
    confidence,
    trend_strength,
    natr,
    vqi
):

    score = (
        confidence * 0.50
        +
        trend_strength * 30
        +
        natr * 10
        +
        vqi * 10
    )

    return round(min(score,100),2)
