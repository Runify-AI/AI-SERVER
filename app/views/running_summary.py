import os
import json
from flask import Blueprint, request, jsonify
from app.models.models import db, Feedback


route_bp = Blueprint("running_summary", __name__)

@route_bp.route("/api/running/summary", methods=["GET"])
def get_running_summary():
    user_id = request.args.get("user_id")
    print(f"요약 요청: user_id={user_id}")

    # record_data.txt 경로
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "record_data.txt")

    # 데이터 불러오기
    with open(file_path, "r", encoding="utf-8") as f:
        run_data = json.load(f)

    # 첫 번째 기록만 사용
    track_points = run_data["historys"][0]["history"]["runningTrackPoint"]

    # 총 거리 (m → km)
    total_distance_m = sum(p.get("distance", 0) for p in track_points)
    total_distance_km = round(total_distance_m / 1000, 2)

    # 총 시간 (프레임 개수 기준)
    duration = len(track_points)

    # 평균 페이스 (분/km)
    averagePace = sum(p.get("pace", 0) for p in track_points) / max(duration, 1)

    # 정지 횟수: pace가 0일 때
    stopCount = sum(1 for p in track_points if p.get("pace", 0) == 0)

    # 러닝 집중도: 멈추지 않은 시간 비율 (%)
    moving_count = duration - stopCount
    focusScore = round((moving_count / duration) * 100, 1)  # %

    # 초반과 후반 평균 pace 비교
    first_n = track_points[:5]
    last_n = track_points[-5:]

    early_avg = sum(p.get("pace", 0) for p in first_n) / max(len(first_n), 1)
    late_avg = sum(p.get("pace", 0) for p in last_n) / max(len(last_n), 1)
    pace_diff = abs(early_avg - late_avg)

    # 전체 평균 pace와 초반의 편차 계산
    total_avg = sum(p.get("pace", 0) for p in track_points) / max(len(track_points), 1)
    deviation = round(abs(early_avg - total_avg), 2)

    # 피드백 요약
    if deviation < 0.5:
        main = "오늘 러닝은 안정적이었어요!"
        advice = "지금처럼 유지해보세요!"
    else:
        main = "초반과 후반 속도 차이가 있어요."
        advice = "다음엔 초반 속도를 더 조절해보세요."

    return jsonify({
        "distance": total_distance_km,
        "duration": duration,
        "averagePace": round(averagePace, 1),
        "stopCount": stopCount,
        "focusScore": focusScore,
        "feedbackSummary": {
            "main": main,
            "advice": advice,
            "early_speed_deviation": deviation
        }
    })


@route_bp.route("/api/running/feedback", methods=["POST"])
def submit_running_feedback():
    data = request.get_json()
    print(f"피드백 수신: {data}")

    feedback = Feedback(
        user_id=data["user_id"],
        rating=data["rating"],
        recommend=data["recommend"],
        comment=data["comment"],
        completed_at=data["completed_at"]
    )

    db.session.add(feedback)
    db.session.commit()

    return jsonify({ "status": "ok", "message": "피드백이 저장되었습니다." })
