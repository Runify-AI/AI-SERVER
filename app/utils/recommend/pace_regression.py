# app/recommend/pace_regression.py
from sklearn.linear_model import LinearRegression

def train_pace_model(df):
    X = df[[
        "distance_km", "stop_rate", "focus_score", "effort_level",
        "early_speed_dev", "temp_c", "humidity", "time_sin", "time_cos"
    ]]
    y = df["averagePace"]

    model = LinearRegression()
    model.fit(X, y)
    return model


def predict_pace(model, row):
    if model is None:
        return row["averagePace"]  # fallback

    X = row[[
        "distance_km", "stop_rate", "focus_score", "effort_level",
        "early_speed_dev", "temp_c", "humidity", "time_sin", "time_cos"
    ]].values.reshape(1, -1)

    return float(model.predict(X)[0])

type_base_pace = {
        "JOGGING": 7.5,
        "RUNNING": 6.0,
        "HALF_MARATHON": 5.5,
        "TRAIL_RUNNING": 7.0,
        "INTERVAL_TRAINING": 4.8,
}

def apply_user_for_pace(base_pace,user):
    height_m = user["height"] / 100 
    weight = user["weight"]
    running_type = user["runningType"]
    
    if (running_type and running_type in type_base_pace):
        base_pace =  type_base_pace[running_type]

    # BMI 계산
    bmi = weight / (height_m ** 2)

    # 보정 계수
    # BMI가 22(정상)일 때 pace=6.0
    # BMI 높으면 느려지고, 낮으면 빨라짐
    diff = bmi - 22
    pace = base_pace + diff * 0.08  # BMI 1 증가당 약 5초 차이

    # 최솟값/최댓값 제한
    pace = max(4.5, min(pace, 9.0))
    return round(pace, 2)

def apply_weather_fore_pace(base_pace, weather):
    temp = weather.get("temperature", 20)
    humidity = weather.get("humidity", 50)

    # 온도 보정: 20도 기준, ±10도당 0.2분/km 변화
    base_pace += (temp - 20) * 0.02
    # 습도 보정: 60% 기준, ±20%당 0.1분/km 변화
    base_pace += (humidity - 60) * 0.005

    return round(max(4.5, min(base_pace, 9.0)), 2)