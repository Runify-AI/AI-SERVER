from flask import Flask
from flask_cors import CORS
from app.prefix_middleware import PrefixMiddleware
from app.models.models import db
from app.views.running_summary import route_bp as summary_bp
import pymysql
pymysql.install_as_MySQLdb()

def create_app():
    app = Flask(__name__)


    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['SECRET_KEY'] = 'secret!'

    # DB 설정( 변경 필요 )
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost:3306/runify_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/api/ai')


    @app.route("/test")
    def getTest():
        return {"test": True}

    app.register_blueprint(summary_bp)

    return app
