def financial_strength(
    rsi,
    trend_strength,
    volatility
):

    score = 0

    if 40 <= rsi <= 70:
        score += 1

    if trend_strength > 0.30:
        score += 1

    if volatility > 1:
        score += 1

    if score == 3:
        return "STRONG"

    elif score == 2:
        return "MODERATE"

    else:
        return "WEAK"
