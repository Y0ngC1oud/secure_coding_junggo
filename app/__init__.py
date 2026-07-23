import os

from flask import Flask

from .config import Config
from .extensions import csrf, db, limiter, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    _ensure_runtime_dirs(app)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    from . import models  # noqa: F401  (User 로더 등록 전 모델 로드 필요)

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    from .auth.routes import auth_bp
    from .chat.routes import chat_bp
    from .main.routes import main_bp
    from .products.routes import products_bp
    from .reports.routes import reports_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(reports_bp)

    with app.app_context():
        db.create_all()

    return app


def _ensure_runtime_dirs(app):
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if db_uri.startswith("sqlite:///"):
        os.makedirs(os.path.dirname(db_uri.replace("sqlite:///", "")), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
