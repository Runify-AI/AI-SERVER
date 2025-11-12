
from app.utils.recommend import *

def recommend_paths(paths, req_json):
    
    # 과거 기록
    history = req_json["history"]
    
    # 유저 선호
    preferences = req_json["user_profile"]["preferences"]
    
    # 날씨 정보
    weather = req_json["weather"]
    
    # 유저 정보
    user = req_json["user_profile"]

    # 히스토리 3개 이하시 기본 추천 로직
    if (history is None) or (len(history) < 3):
        return base_recommend_paths(paths, preferences,weather,user)
    
    df = []

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

    return results

'''
refacor version 1.0
에러 사항 :  history가 없는 사용자
수정 사항
-> 초기 히스토리 없는 사용자의 경우 기본 페이스, 유저 프로필 기반으로 추천 점수 산출
'''

def base_recommend_paths(paths, preferences,weather,user=None):
    results = []
    for path in paths:
        feature = path["feature"]
        feature['distance'] = path['distance']

        preference_score = compute_preference_score(feature, preferences)

        # 기본 페이스 점수 (거리 기반)
        
        base_pace =  6.0  # 기본 페이스 (분/km)
        base_pace = apply_user_for_pace(base_pace,user)
        base_pace = apply_weather_fore_pace(base_pace, weather)
        pace_score = compute_pace_score(base_pace, base_pace)

        final_score = compute_final_score(preference_score, pace_score)

        results.append({
            **path,
            "recommend" : {
                "recommended_pace": round(base_pace, 2),
                "expected_time": round(path["distance"] * base_pace, 1),
                "preference_score": round(preference_score, 3),
                "pace_score": round(pace_score, 3),
                "final_score": round(final_score, 3)
            }
        })

    results.sort(key=lambda x: x["recommend"]["final_score"], reverse=True)

    return results
    