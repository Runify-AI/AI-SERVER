# app/recommend/pace_regression.py
from sklearn.linear_model import LinearRegression

def train_pace_model(df):
    if len(df) < 3:
        # 기록 부족 → 마지막 pace 그대로 사용하는 fallback
        return None

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
