from flask_restx import Namespace, fields

route_ns = Namespace('route', description='route api')

# 위치 정보
location_model = route_ns.model('Location', {
    'latitude': fields.Float(required=True, description='위도', example=35.8310738),
    'longitude': fields.Float(required=True, description='경도', example=128.7495178)
})

# 러닝 트랙 포인트
running_track_point_model = route_ns.model('RunningTrackPoint', {
    'distance': fields.Float(required=True, example=0.1),
    'elapsedTime': fields.Float(required=True, example=300.0),
    'typeEta': fields.Float(required=True, example=0.1),
    'typePace': fields.Float(required=True, example=0.1),
    'typeStop': fields.Float(required=True, example=0.1),
    'location': fields.Nested(location_model, required=True, example={
        "latitude": 35.8310738,
        "longitude": 128.7495178
    }),
    'pace': fields.Float(required=True, example=5.0),
    'timeStamp': fields.Float(required=True, example=1624356000.0)
})

# 러닝 히스토리
history_model = route_ns.model('History', {
    'routeId': fields.Integer(required=False, example=1),
    'runId': fields.String(required=False, example="run123"),
    'date': fields.String(required=True, example="2025-06-22"),
    'totalDistance': fields.Integer(required=True, example=5000),
    'averagePace': fields.Float(required=True, example=5.2),
    'effortLevel': fields.Integer(required=True, example=3),
    'comment': fields.String(required=True, example="Good run!"),
    'runningTrackPoint': fields.List(
        fields.Nested(running_track_point_model),
        required=True,
        example=[
            {
                "distance": 0.1,
                "elapsedTime": 300.0,
                "typeEta": 0.1,
                "typePace": 0.1,
                "typeStop": 0.1,
                "location": {
                    "latitude": 35.8310738,
                    "longitude": 128.7495178
                },
                "pace": 5.0,
                "timeStamp": 1624356000.0
            }
        ]
    )
})

# 선호도
preferences_model = route_ns.model('Preferences', {
    'preferencePlace': fields.List(fields.String, required=True, example=["park", "river"]),
    'preferenceRoute': fields.List(fields.String, required=True, example=["scenic"]),
    'preferenceAvoid': fields.List(fields.String, required=True, example=["hill"]),
    'preferenceEtc': fields.List(fields.String, required=True, example=["morning"])
})

# 유저 프로필
user_profile_model = route_ns.model('UserProfile', {
    'runningType': fields.String(required=True, example="marathon"),
    'height': fields.Float(required=True, example=175.5),
    'weight': fields.Float(required=True, example=68.0),
    'preferences': fields.Nested(preferences_model, required=True, example={
        "preferencePlace": ["park", "river"],
        "preferenceRoute": ["scenic"],
        "preferenceAvoid": ["hill"],
        "preferenceEtc": ["morning"]
    })
})

# 날씨
weather_model = route_ns.model('Weather', {
    'temperature': fields.Float(required=True, example=22.5),
    'humidity': fields.Integer(required=True, example=60),
    'condition': fields.String(required=True, example="Cloudy")
})

# 최상위 요청 DTO
request_model = route_ns.model('RouteRequest', {
    'userProfile': fields.Nested(user_profile_model, required=True, example={
        "runningType": "marathon",
        "height": 175.5,
        "weight": 68.0,
        "preferences": {
            "preferencePlace": ["park", "river"],
            "preferenceRoute": ["scenic"],
            "preferenceAvoid": ["hill"],
            "preferenceEtc": ["morning"]
        }
    }),
    'history': fields.List(fields.Nested(history_model), required=True, example=[
        {
            "routeId": 1,
            "runId": "run123",
            "date": "2025-06-22",
            "totalDistance": 5000,
            "averagePace": 5.2,
            "effortLevel": 3,
            "comment": "Good run!",
            "runningTrackPoint": [
                {
                    "distance": 0.1,
                    "elapsedTime": 300.0,
                    "typeEta": 0.1,
                    "typePace": 0.1,
                    "typeStop": 0.1,
                    "location": {
                        "latitude": 35.8310738,
                        "longitude": 128.7495178
                    },
                    "pace": 5.0,
                    "timeStamp": 1624356000.0
                }
            ]
        }
    ]),
    'weather': fields.Nested(weather_model, required=True, example={
        "temperature": 22.5,
        "humidity": 60,
        "condition": "Cloudy"
    })
})

# 특성(feature) 하위 모델
park_feature_model = route_ns.model('ParkFeature', {
    'count': fields.Integer,
    'area': fields.Integer,
    'ratio': fields.String
})

river_feature_model = route_ns.model('RiverFeature', {
    'count': fields.Integer,
    'area': fields.Integer,
    'ratio': fields.String
})

amenity_feature_model = route_ns.model('AmenityFeature', {
    'count': fields.Integer
})

cross_feature_model = route_ns.model('CrossFeature', {
    'count': fields.Integer
})

# Feture 모델 (오타 반영)
feture_model = route_ns.model('Feture', {
    'park': fields.Nested(park_feature_model),
    'river': fields.Nested(river_feature_model),
    'amenity': fields.Nested(amenity_feature_model),
    'cross': fields.Nested(cross_feature_model)
})

# 추천(recommend) 모델
recommend_model = route_ns.model('Recommend', {
    'similarity': fields.Float,
    'pace_score': fields.Float,
    'final_score': fields.Float,
    'recommended_pace': fields.Float,
    'expected_time': fields.Integer
})

path_model = route_ns.model('Path', {
    'path-id': fields.Integer,
    'feture': fields.Nested(feture_model),
    'recommend': fields.Nested(recommend_model),
    'coord': fields.List(fields.List(fields.Float))
})


# 최상위 응답 모델
response_model = route_ns.model('RouteResponse', {
    'paths': fields.List(fields.Nested(path_model))
})



from typing import Tuple, Dict, Union
import osmnx as ox


class UserInput:
    def __init__(
        self,
        start_address :str,
        end_address : str,
        # arrival_time: str,  # "HH:MM" 형식으로 받음
        # preferences: Dict[str, Union[str, list]]
    ):
        self.start_address = start_address,
        self.end_address = end_address,
        self.start_location = geocode(self.start_address)
        self.end_location = geocode(self.end_address)
        # self.arrival_time = arrival_time
        # self.preferences = preferences

    def __repr__(self):
        return (
            f"UserInput(start={self.start_location}, end={self.end_location}"
        )
        
def geocode(address):
    return ox.geocoder.geocode(address)