from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp


class RegisterForm(FlaskForm):
    username = StringField(
        "아이디",
        validators=[
            DataRequired(message="아이디를 입력해주세요."),
            Length(min=4, max=20, message="아이디는 4~20자여야 합니다."),
            Regexp(r"^[a-zA-Z0-9_]+$", message="아이디는 영문, 숫자, 밑줄(_)만 사용할 수 있습니다."),
        ],
    )
    nickname = StringField(
        "닉네임",
        validators=[DataRequired(message="닉네임을 입력해주세요."), Length(min=2, max=20)],
    )
    password = PasswordField(
        "비밀번호",
        validators=[DataRequired(message="비밀번호를 입력해주세요."), Length(min=8, max=100, message="비밀번호는 8자 이상이어야 합니다.")],
    )
    password_confirm = PasswordField(
        "비밀번호 확인",
        validators=[DataRequired(), EqualTo("password", message="비밀번호가 일치하지 않습니다.")],
    )
