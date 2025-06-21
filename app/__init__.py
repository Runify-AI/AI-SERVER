from flask import Flask
from flask_cors import CORS
from app.prefix_middleware import PrefixMiddleware

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['SECRET_KEY'] = 'secret!'
    
    # 라우터 prefix 고정시키기
    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/api/ai')
    
    @app.route("/test")
    def getTest():
        return {"test":True}
    
    # 라우터 등록하기
    # router_bp
    # statics_bp
    
    return app
