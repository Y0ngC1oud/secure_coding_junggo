import os

import click
from flask import Flask
from flask_login import current_user, logout_user

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

    from .admin.routes import admin_bp
    from .auth.routes import auth_bp
    from .chat.routes import chat_bp
    from .main.routes import main_bp
    from .products.routes import products_bp
    from .reports.routes import reports_bp
    from .transfers.routes import transfers_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(transfers_bp)
    app.register_blueprint(admin_bp)

    @app.before_request
    def enforce_active_status():
        # 로그인 중인 사용자가 관리자에 의해 정지/휴면 처리되면 다음 요청에서 즉시 세션을 종료
        if current_user.is_authenticated and current_user.status != "active":
            logout_user()

    @app.cli.command("create-admin")
    @click.argument("username")
    def create_admin(username):
        """지정한 아이디의 사용자를 관리자 권한으로 승격합니다."""
        user = models.User.query.filter_by(username=username).first()
        if user is None:
            click.echo(f"사용자 '{username}'를 찾을 수 없습니다.")
            return
        user.role = "admin"
        db.session.commit()
        click.echo(f"'{username}' 님을 관리자로 지정했습니다.")

    with app.app_context():
        db.create_all()

    return app


def _ensure_runtime_dirs(app):
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if db_uri.startswith("sqlite:///"):
        os.makedirs(os.path.dirname(db_uri.replace("sqlite:///", "")), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
