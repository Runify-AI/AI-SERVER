
from app.utils.recommend import *

def recommend_paths(paths, req_json):
    
    # 과거 기록
    history = req_json["history"]

    # 유저 선호
    preferences = req_json["user_profile"]["preferences"]

    # 날씨 정보
    weather = req_json["weather"]

    df = extract_history_features(history, weather)

    print(df)
    model = train_pace_model(df)


    recent_pace = df["averagePace"].iloc[-1]

    results = []
    for path in paths:
        feature = path["feature"]
        feature['distance'] = path['distance']

        preference_score = compute_preference_score(feature, preferences)

        # pace 예측
        row = df.iloc[-1].copy()
        row["distance"] = path["distance"]
        predicted_pace = predict_pace(model, row)

        print("예측 결과 : ", predicted_pace)
        pace_score = compute_pace_score(predicted_pace, recent_pace)

        final_score = compute_final_score(preference_score, pace_score)

        results.append({
            **path,
            "recommend" : {
                "recommended_pace": round(predicted_pace, 2),
                "expected_time": round(path["distance"] * predicted_pace, 1),
                "preference_score": round(preference_score, 3),
                "pace_score": round(pace_score, 3),
                "final_score": round(final_score, 3)
            }
        })

    results.sort(key=lambda x: x["recommend"]["final_score"], reverse=True)

    print("최종 result : ", results[0])
    return results
