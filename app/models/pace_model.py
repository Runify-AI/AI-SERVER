import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

def _encode_time_of_day(ts):
    hour = ts.dt.hour + ts.dt.minute/60
    rad = 2 * np.pi * hour / 24
    return np.sin(rad), np.cos(rad)

def build_user_pace_training_frame(running_df, weather_df):
    df = running_df.copy()
    df["target"] = df["pace_min_per_km"]

    sin_t, cos_t = _encode_time_of_day(df["timestamp"])
    df["time_sin"] = sin_t
    df["time_cos"] = cos_t

    df = pd.merge_asof(
        df.sort_values("timestamp"),
        weather_df.sort_values("timestamp"),
        on="timestamp",
        direction="nearest"
    ).fillna(df.mean(numeric_only=True))

    features = [
        "distance_km", "duration_min", "stop_rate",
        "focus_score", "effort_level", "early_speed_dev",
        "temp_c", "humidity", "time_sin", "time_cos"
    ]

    return df[features + ["target"]]

def train_user_pace_model(train_df):
    X = train_df.drop(columns=["target"]).values
    y = train_df["target"].values
    model = Pipeline([
        ("poly", PolynomialFeatures(degree=2, include_bias=False)),
        ("ridge", Ridge(alpha=1.0))
    ])
    model.fit(X, y)
    return model

def predict_expected_pace(model, x_vec):
    pred = model.predict([x_vec])[0]
    return float(np.clip(pred, 3.0, 12.0))
