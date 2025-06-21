from flask_restx import Namespace, Resource

test_ns = Namespace('test', description='테스트 네임스페이스')

@test_ns.route('/')
class TestResource(Resource):
    def get(self):
        return {"test": True}