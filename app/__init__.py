from flask import Flask
from flask_cors import CORS
from app.prefix_middleware import PrefixMiddleware
from app.views.test_views import test_ns
from app.views.route_views import route_ns

from flask_restx import Api, Resource, reqparse

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['SECRET_KEY'] = 'secret!'
    
    #swagger 등록하기
    
    api = Api(app ,version='1.0', title='API 문서',
              description='Swagger 문서', doc="/docs")
    
    # 라우터 prefix 고정시키기
    app.wsgi_app = PrefixMiddleware(
        app.wsgi_app,
        prefix='/api/ai',
    )
    
    # 라우터 등록하기
    api.add_namespace(test_ns, path='/test')
    api.add_namespace(route_ns, path="/route")
    # statics_bp
    
    return app
