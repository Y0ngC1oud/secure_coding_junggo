from flask import Blueprint, current_app, flash, redirect, render_template, url_for

from ..extensions import db
from ..models import User
from .forms import RegisterForm

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
        return redirect(url_for("main.home"))

    return render_template("auth/register.html", form=form)
