import math

def compute_pace_score(predicted_pace, recent_pace):
    diff = abs(predicted_pace - recent_pace)
    return math.exp(-diff * 0.35)  # diff가 작을수록 높은 점수


def compute_final_score(preference_score, pace_score):
    # MEDIUM = 50% + 50%
    return 0.5 * preference_score + 0.5 * pace_score
