from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db, limiter
from ..models import User
from .forms import LoginForm, RegisterForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing = User.query.filter_by(username=form.username.data).first()
        if existing:
            flash("이미 사용 중인 아이디입니다.", "error")
            return render_template("auth/register.html", form=form)

        user = User(
            username=form.username.data,
            nickname=form.nickname.data,
            balance=current_app.config["STARTING_BALANCE"],
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("회원가입이 완료되었습니다. 로그인해주세요.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")
            return render_template("auth/login.html", form=form)

        if user.status != "active":
            flash("정지되었거나 휴면 처리된 계정입니다. 관리자에게 문의하세요.", "error")
            return render_template("auth/login.html", form=form)

        login_user(user)
        flash(f"{user.nickname}님, 환영합니다.", "success")
        return redirect(url_for("main.home"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("로그아웃되었습니다.", "info")
    return redirect(url_for("main.home"))
