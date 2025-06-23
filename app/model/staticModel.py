from flask_restx import Namespace, fields

statics_ns = Namespace('statics', description='statics api')

running_track_model = statics_ns.model('RunningTrack',{
    'distance': fields.Float(required=True,example=55.59),
    'elapsedTime': fields.Float(example=3),
    'pace': fields.Float(example=4.3)
})

request_model = statics_ns.model('StaticRequest',{
    'history': fields.List(fields.Nested(running_track_model),example=[
        
          {
            "distance": 55.59746332254485,
            "elapsedTime": 3,
            "pace": 0.8993216059144363,
          },
          {
            "distance": 55.59746332254485,
            "elapsedTime": 6,
            "pace": 1.7986432118288727,
          },
          {
            "distance": 55.59746332254485,
            "elapsedTime": 9,
            "pace": 2.697964817743309,
          },
          {
            "distance": 45.060062095528956,
            "elapsedTime": 12,
            "pace": 4.4385202926705425,
          },
          {
            "distance": 45.058925233573156,
            "elapsedTime": 15,
            "pace": 5.548290348783694,
          },
          {
            "distance": 55.59746332254485,
            "elapsedTime": 18,
            "pace": 5.395929635486618,
          },
          {
            "distance": 55.59746332254485,
            "elapsedTime": 21,
            "pace": 6.295251241401053,
            "timeStamp": 1750067643065
          },
          {
            "distance": 45.05324010027789,
            "elapsedTime": 24,
            "pace": 8.878384753453787,
          },
    ])
})

feedback_model = statics_ns.model('FeedBack',{
    'main':fields.String(example="초반과 후반 속도 차이가 있어요"),
    'advice':fields.String(example="다음엔 초반 속도를 조절해보세요"),
    "early_speed_deviation":fields.Integer(example=78)
})

static_model = statics_ns.model('Statics', {
    'distance': fields.Integer(required=True, example=0.41),
    'averagePace': fields.Float(required=True, example=4.5),
    'dutration': fields.Float(required=True,example=50),
    'stopCount': fields.Integer(required=True, example=3),
    'feedbackSummary' : fields.Nested(feedback_model,example= {
                "main": "초반과 후반 속도 차이가 있어요.",  
                "advice": "다음엔 초반 속도를 더 조절해보세요.",
                "early_speed_deviation": 1.2 
            }),
    'focusScore' : fields.Float(requiredd=True,example=78),
})

response_model = statics_ns.model('StaticResponse',{
    'statics' : fields.Nested(static_model, example={
        "statics": {
            "distance": 0.41,
            "duration": 8,
            "averagePace": 4.5,
            "stopCount": 0,
            "focusScore": 100,
            "feedbackSummary": {
                "main": "초반과 후반 속도 차이가 있어요.",
                "advice": "다음엔 초반 속도를 더 조절해보세요.",
                "early_speed_deviation": 1.42
            }
        }
    })
})