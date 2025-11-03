
def compute_preference_score(path_feature, preferences):
    score = 0

    # MEDIUM = 선호 영향 0.5 스케일
    SCALE = 0.5

    # 장소 선호 (PARK / RIVER)
    if "PARK" in preferences["preferencePlaces"]:
        score += SCALE * float(path_feature["park"]["ratio"] / 100)
    if "RIVER" in preferences["preferencePlaces"]:
        score += SCALE * float(path_feature["river"]["ratio"]/100)

    # 빠른 길 선호 -> distance가 짧을수록 score 높음
    if "FASTEST" in preferences["preferenceRoutes"]:
        score += SCALE * (1 / max(path_feature["distance"], 0.2))

    # 언덕 회피 -> slope가 크면 감점
    if "HILL" in preferences["preferenceAvoids"]:
        slope = path_feature.get("slope", 0)
        score -= SCALE * slope

    return score
