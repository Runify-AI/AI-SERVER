from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['SECRET_KEY'] = 'secret!'
    
    # 라우터 등록하기
    # router_bp
    # statics_bp
    
    return app
