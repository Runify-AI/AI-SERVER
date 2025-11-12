import requests
import statistics
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일의 변수들을 환경변수로 로드
api_key = os.getenv("google_api_key")


def coord_getLabel(coords):
    if not coords:
        return None

    # 1️⃣ 중심점 계산
    lat = statistics.mean([c[0] for c in coords])
    lng = statistics.mean([c[1] for c in coords])

    # 2️⃣ 검색 반경 (m 단위)
    radius = 100

    # 3️⃣ 검색할 주요 type 목록
    types = ["park", "river", "crossing", "store", "cafe", "gym", "convenience_store"]

    summary = {
        "park": {"count": 0},
        "river": {"count": 0},
        "cross": {"count": 0},
        "amenity": {"count": 0}
    }

    # 4️⃣ 각 type별 API 호출
    for t in types:
        url = (
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
            f"location={lat},{lng}&radius={radius}&type={t}&key={api_key}"
        )
        resp = requests.get(url)
        data = resp.json()

        if "results" not in data:
            continue

        count = len(data["results"])

        if t == "park":
            summary["park"]["count"] += count
        elif t == "river":
            summary["river"]["count"] += count
        elif t == "crossing":
            summary["cross"]["count"] += count
        else:
            summary["amenity"]["count"] += count

    return summary
