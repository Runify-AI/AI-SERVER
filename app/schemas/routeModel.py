from flask_restx import Namespace, fields
from numpy.f2py.crackfortran import requiredpattern

route_ns = Namespace('route', description='route api')

feedback_model = route_ns.model('FeedBack',{
    'main':fields.String(example="초반과 후반 속도 차이가 있어요"),
    'advice':fields.String(example="다음엔 초반 속도를 조절해보세요"),
    "early_speed_deviation":fields.Float(example=78)
})

# 러닝 히스토리
history_model = route_ns.model('History', {
    'routeId': fields.Integer(required=False, example=1),
    'date': fields.String(required=True, example="2025-06-22"),
    'distance': fields.Float(required=True, example=5000),
    'averagePace': fields.Float(required=True, example=5.2),
    'effortLevel': fields.Integer(required=True, example=3),
    'stopCount': fields.Integer(required=True, example=3),
    'feedbackSummary' : fields.Nested(feedback_model,example= {
                "main": "초반과 후반 속도 차이가 있어요.",  
                "advice": "다음엔 초반 속도를 더 조절해보세요.",
                "early_speed_deviation": 1.2 
            }),
    'focusScore' : fields.Float(requiredd=True,example=78),
    'comment': fields.String(required=True, example="Good run!"),
})

# 선호도
preferences_model = route_ns.model('Preferences', {
    'preferencePlace': fields.List(fields.String, required=True, example=["park", "river"]),
    'preferenceRoute': fields.List(fields.String, required=True, example=["scenic"]),
    'preferenceAvoid': fields.List(fields.String, required=True, example=["hill"]),
    'preferenceEtc': fields.List(fields.String, required=True, example=["morning"])
})

# 유저 프로필
user_profile_model = route_ns.model('user_profile', {
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
weather_model = route_ns.model('weather', {
    'temperature': fields.Float(required=True, example=22.5),
    'humidity': fields.Integer(required=True, example=60),
    'condition': fields.String(required=True, example="Cloudy")
})

pos = route_ns.model('pos',{
    "latitude" : fields.Float(required=True),
    "longitude" : fields.Float(required=True),
    "name"  : fields.String(required=False)
})

# 최상위 요청 DTO
request_model = route_ns.model('RouteRequest', {
    "startAddr" : fields.Nested(pos,required=True,example={"latitude" : 35.865403, "longitude" : 128.593636, "name" : "반월당"}),
    "endAddr" : fields.Nested(pos,required=False,example={"latitude" : 35.827883, "longitude" : 128.755046, "name" : "영남대학교"}),
    'user_profile': fields.Nested(user_profile_model, required=True, example={
        "runningType": "marathon",
        "height": 175.5,
        "weight": 68.0,
        "preferences": {
            "preferencePlaces": ["PARK", "RIVER"],
            "preferenceRoutes": ["FASTEST",],
            "preferenceAvoids": ["HILL"],
            "preferenceEtcs": ["PET","ACCESSIBLE"]
        }
    }),
    'history': fields.List(fields.Nested(history_model), required=True, example=[
        {
            "routeId": 1,
            "date": "2025-06-22",
            "distance": 3.21,
            "duration":25,
            "averagePace": 5.2,
            "stopCount": 3,
            "feedbackSummary": {
                "main": "초반과 후반 속도 차이가 있어요.",  
                "advice": "다음엔 초반 속도를 더 조절해보세요.",
                "early_speed_deviation": 1
            },
            "focusScore": 78,
            "effortLevel": 3,
            "comment": "Good run!",
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
    'area': fields.Float,
    'ratio': fields.Float
})

river_feature_model = route_ns.model('RiverFeature', {
    'count': fields.Integer,
    'area': fields.Float,
    'ratio': fields.Float
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
    'pace_score': fields.Float,
    'final_score': fields.Float,
    'preference_score' : fields.Float,
    'recommended_pace': fields.Float,
    'expected_time': fields.Integer
})

path_model = route_ns.model('Path', {
    'pathId': fields.Integer,
    'feature': fields.Nested(feture_model),
    'distance' : fields.Float(),
    'slope' : fields.Float(),
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
    ):
        self.start_address = start_address,
        self.end_address = end_address,
        self.start_location = geocode(self.start_address)
        self.end_location = geocode(self.end_address) if end_address != "" else None
        # self.arrival_time = arrival_time
        # self.preferences = preferences

    def __repr__(self):
        return (
            f"UserInput(start={self.start_location}, end={self.end_location}"
        )
        
def geocode(address):
    return ox.geocoder.geocode(address)