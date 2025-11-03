import math
import pandas as pd
from datetime import datetime

def extract_history_features(history, weather):
    """
    history: list of user run records
    weather: {temperature, humidity, condition}
    return: pandas DataFrame
    """

    rows = []
    for run in history:
        distance_km = run["distance"]
        duration_min = run["duration"]
        stop_rate = run["stopCount"] / max(distance_km, 0.1)

        focus_score = run["focusScore"]
        effort_level = run["effortLevel"]
        early_speed_dev = run["feedbackSummary"].get("early_speed_deviation", 0)

        temp_c = weather["temperature"]
        humidity = weather["humidity"]

        # 러닝 시간대 → sin/cos 변환
        dt = datetime.fromisoformat(run["date"])
        hour = dt.hour + dt.minute / 60
        time_sin = math.sin(2 * math.pi * hour / 24)
        time_cos = math.cos(2 * math.pi * hour / 24)

        rows.append({
            "distance_km": distance_km,
            "duration_min": duration_min,
            "stop_rate": stop_rate,
            "focus_score": focus_score,
            "effort_level": effort_level,
            "early_speed_dev": early_speed_dev,
            "temp_c": temp_c,
            "humidity": humidity,
            "time_sin": time_sin,
            "time_cos": time_cos,
            "averagePace": run["averagePace"]
        })


    return pd.DataFrame(rows)
