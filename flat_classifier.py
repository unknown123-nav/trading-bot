def classify_flat_market(
        trend_strength,
        bb_width
):

    if trend_strength < 0.15:
        return "FLAT"

    elif bb_width < 2:
        return "SIDEWAYS"

    return "TRENDING"
