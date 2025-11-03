def preference_weight(p, pref):
    score = 0.0

    for v in pref["preferencePlaces"]:
        if v == "PARK": score += p["park_ratio"] * 1.2
        if v == "RIVER": score += p["river_ratio"] * 1.2
        if v == "CAFE": score += p["amenity_count"] * 0.6

    for v in pref["preferenceRoutes"]:
        if v == "FASTEST": score += (1 / (1 + p["cross_count"])) * 1.3
        if v == "SCENIC": score += (p["park_ratio"] + p["river_ratio"]) * 1.1
        if v == "EXERCISE": score += (p["cross_count"] / 20) * 1.2
        if v == "QUIET": score += (1 - p["cross_count"] / 20) * 1.4

    for v in pref["prefereneAvoids"]:
        if v == "FASTEST": score += (1 / (1 + p["cross_count"])) * 1.3
        if v == "SCENIC": score += (p["park_ratio"] + p["river_ratio"]) * 1.1
        if v == "EXERCISE": score += (p["cross_count"] / 20) * 1.2
        if v == "QUIET": score += (1 - p["cross_count"] / 20) * 1.4

    for v in pref["preferenceEtcs"]:
        if v == "CONVENIENCE": score += p["amenity_count"] * 0.5

    return score
