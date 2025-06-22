from flask import request
from flask_restx import Resource,reqparse
from app.model.staticModel import statics_ns,request_model,response_model

@statics_ns.route('/')
class StaticResource(Resource):
    @statics_ns.expect(request_model)
    @statics_ns.marshal_with(response_model)
    def post(self):
        return {"statics":getStatics(request.get_json()["history"])}
    
def getStatics(history):
        # 총 거리 (m → km)
    total_distance_m = sum(p.get("distance", 0) for p in history)
    total_distance_km = round(total_distance_m / 1000, 2)

    # 총 시간 (프레임 개수 기준)
    duration = len(history)

    # 평균 페이스 (분/km)
    avg_pace = sum(p.get("pace", 0) for p in history) / max(duration, 1)

    # 정지 횟수: pace가 0일 때
    stop_count = sum(1 for p in history if p.get("pace", 0) == 0)

    # 러닝 집중도: 멈추지 않은 시간 비율 (%)
    moving_count = duration - stop_count
    focus_rate = round((moving_count / duration) * 100, 1)  # %

    # 초반과 후반 평균 pace 비교
    first_n = history[:5]
    last_n = history[-5:]

    early_avg = sum(p.get("pace", 0) for p in first_n) / max(len(first_n), 1)
    late_avg = sum(p.get("pace", 0) for p in last_n) / max(len(last_n), 1)
    pace_diff = abs(early_avg - late_avg)

    # 전체 평균 pace와 초반의 편차 계산
    total_avg = sum(p.get("pace", 0) for p in history) / max(len(history), 1)
    deviation = round(abs(early_avg - total_avg), 2)

    # 피드백 요약 생성
    if deviation < 0.5:
        main = "오늘 러닝은 안정적이었어요!"
        advice = "지금처럼 유지해보세요!"
    else:
        main = "초반과 후반 속도 차이가 있어요."
        advice = "다음엔 초반 속도를 더 조절해보세요."

    return {
        "distance": total_distance_km,
        "duration": duration,
        "averagePace": round(avg_pace, 1),
        "stop_count": stop_count,
        "focus_score": focus_rate,
        "feedback_summary": {
            "main": main,
            "advice": advice,
            "early_speed_deviation": deviation
        }
    }